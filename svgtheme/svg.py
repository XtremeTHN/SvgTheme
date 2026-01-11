# modified version of https://www.reddit.com/r/unixporn/comments/1q6ngwh/oc_auto_svg_icon_recolorer_to_match_every_icon_to/
# i just copied and refactored the class that recolors the svgs
from typing import Generator, Sequence, SupportsInt, Tuple, Set
from xml.dom import minidom
from pathlib import Path
import re


class SvgRecolorer:
    NAMED_COLORS = {
        "black": "#000000",
        "white": "#ffffff",
        "red": "#ff0000",
        "green": "#008000",
        "blue": "#0000ff",
        "yellow": "#ffff00",
        "gray": "#808080",
        "grey": "#808080",
        "silver": "#c0c0c0",
        "maroon": "#800000",
        "purple": "#800080",
        "fuchsia": "#ff00ff",
        "lime": "#00ff00",
        "olive": "#808000",
        "navy": "#000080",
        "teal": "#008080",
        "aqua": "#00ffff",
    }

    def __init__(self, colors: Sequence[str], mono_color: str):
        self.colors: list[str] = colors
        self.mono_color = mono_color

    def hex_to_rgb(self, _hex: str) -> Tuple[SupportsInt, ...]:
        try:
            _hex = _hex.lstrip("#")
            if len(_hex) == 3:
                _hex = "".join([c * 2 for c in _hex])
            return tuple(int(_hex[i : i + 2], 16) for i in (0, 2, 4))
        except Exception as e:
            # TODO: check what exception is and handle only that exception
            print(e.__class__.___name__, e.args)
            return (0, 0, 0)

    def rgb_to_hex(self, rgb: Sequence[SupportsInt]) -> str:
        rgb = [int(x) for x in rgb]
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def interpolate_color(self, first: str, second: str, factor: SupportsInt) -> str:
        try:
            rgb1 = self.hex_to_rgb(first)
            rgb2 = self.hex_to_rgb(second)
            rgb = tuple(rgb1[i] + (rgb2[i] - rgb1[i]) * factor for i in range(3))
            return self.rgb_to_hex(rgb)
        except Exception as e:
            # TODO: check what exception is and handle only that exception
            print(e.__class__.___name__, e.args)
            return first

    def is_valid_color(self, color: str):
        if not color:
            return False
        color = color.strip()

        # FIXME: maybe it will skip url, but this script is for svg from icon themes
        invalid = [
            "none",
            "transparent",
            "currentcolor",
            "inherit",
            "url(",
            "rgba(0,0,0,0)",
            "rgba(255,255,255,0)",
        ]

        if color in invalid:
            return False

        return True

    def normalize_color(self, color: str):
        if not color:
            return None
        color = color.strip()

        if color.startswith("rgba"):
            color = color[:3] + color[4:]

        if color.startswith("rgb"):
            c = color.replace(" ")[4:-1].split(",")
            if len(c) > 3:
                c.pop()
            return self.rgb_to_hex(c)

        if color.startswith("#"):
            return color

        return self.NAMED_COLORS.get(color)

    def get_gradient_colors(self, num_colors: SupportsInt) -> Sequence[str]:
        base_colors = self.colors
        num_base_colors = len(base_colors)

        if num_colors <= num_base_colors:
            return base_colors[:num_colors]

        colors = []

        for i in range(num_colors):
            factor = i / (num_colors - 1) if num_colors > 1 else 0

            segment_index = int(factor * (num_base_colors - 1))
            if segment_index >= num_base_colors - 1:
                segment_index = num_base_colors - 2
                segment_factor = 1.0
            else:
                segment_start = segment_index / (num_base_colors - 1)
                segment_end = (segment_index + 1) / (num_base_colors - 1)
                segment_factor = (factor - segment_start) / (
                    segment_end - segment_start
                )

            color_start = base_colors[segment_index]
            color_end = base_colors[segment_index + 1]
            color = self.interpolate_color(color_start, color_end, segment_factor)
            colors.append(color)

        return colors

    def get_xml_doc(self, file: Path) -> minidom.Document:
        svg_content = file.read_text().replace('xmlns="http://www.w3.org/2000/svg"', "")
        return minidom.parseString(svg_content)

    def get_svg_layers(
        self, doc: minidom.Document
    ) -> Tuple[Sequence[Tuple[minidom.Element, str, str, str]], Set[str]]:
        layers = []
        colors_found = set()

        def append(color, *props):
            normalized = self.normalize_color(color)
            if normalized and self.is_valid_color(color):
                layers.append((element, normalized, *props))
                colors_found.add(normalized)

        all_elements = doc.getElementsByTagName("*")

        if not all_elements:
            return layers, colors_found

        for element in all_elements:
            if element.hasAttribute("fill"):
                append(element.getAttribute("fill"), "fill", "fill")

            if element.hasAttribute("stroke"):
                append(element.getAttribute("stroke"), "stroke", "stroke")

            if element.hasAttribute("style"):
                style = element.getAttribute("style")

                fill_match = re.search(r"fill\s*:\s*([^;]+)", style, re.IGNORECASE)

                if fill_match:
                    append(fill_match.group(1).strip(), "style", "fill")

                stroke_match = re.search(r"stroke\s*:\s*([^;]+)", style, re.IGNORECASE)
                if stroke_match:
                    append(stroke_match.group(1).strip(), "style", "stroke")

            if element.hasAttribute("stop-color"):
                append(element.getAttribute("stop-color"), "stop-color", "stop-color")

        return layers, colors_found

    def sub_elem(self, prop: str, new: str, orig: str, style: str):
        return re.sub(
            f"{prop}\\s*{re.escape(orig)}",
            f"{prop}:{new}",
            style,
            flags=re.IGNORECASE,
        )

    def recolor_svg(
        self,
        layers: Sequence[Tuple[minidom.Element, Tuple, str, str]],
        unique_colors: Sequence[str],
        monochrome: bool,
    ) -> None:
        gradient_colors = self.get_gradient_colors(len(unique_colors))
        color_map = dict(zip(unique_colors, gradient_colors))

        for element, original_color, attr_type, _ in layers:
            orig_color = "[^;]+" if monochrome else original_color
            n_color = (
                self.mono_color
                if monochrome
                else color_map.get(original_color, original_color)
            )

            try:
                if attr_type in ["fill", "stroke", "stop-color"]:
                    element.setAttribute(attr_type, n_color)

                if attr_type != "style":
                    continue

                style = element.getAttribute("style")
                style = self.sub_elem("fill", n_color, orig_color, style)
                style = self.sub_elem("stroke", n_color, orig_color, style)

                element.setAttribute("style", style)
            except Exception as e:
                print(f"warning: exception while processing layer: {e.args}")
                continue

    def process_file(self, svg_file: Path) -> str:
        try:
            doc = self.get_xml_doc(svg_file)
        except Exception as e:
            print(f"error while parsing svg: {e.args}")
            return

        layers, colors_found = self.get_svg_layers(doc)

        if not layers:
            raise Exception("No colored layers found")

        unique_colors = sorted(list(colors_found))
        if len(unique_colors) == 0:
            raise Exception("No colors found")

        self.recolor_svg(layers, unique_colors, len(colors_found) <= 1)

        return doc.toxml()
