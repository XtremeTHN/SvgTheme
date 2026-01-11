# mono color acacac
import argparse
import json
import sys

from pathlib import Path
from svgtheme.svg import SvgRecolorer


class Args:
    FILES_OR_DIR: list[Path]
    mono_color: str
    color: list[str]
    recursive: bool
    matugen: Path
    output: Path
    palette: str


def error(*msg, exit_code=1):
    print("error:", *msg)
    sys.exit(exit_code)

def handle_folder(svg, args, folder):
    for file, cnt in svg.process_directory(folder, recursive=args.recursive):
        if args.output:
            (args.output / file.relative_to(folder)).write_text(cnt)
        else:
            file.write_text(cnt)

def handle_file(svg, args, file):
    xml = svg.process_file(file)
    if args.output:
        (args.output / file).write_text(xml)
    else:
        file.write_text(xml)

def run():
    parser = argparse.ArgumentParser("svgtheme", description="Recolors svg icons with the provided colors",)

    parser.add_argument(
        "FILES_OR_DIR",
        nargs="+",
        type=Path,
        help="SVG file or directory containing SVG files to recolor.",
    )
    parser.add_argument(
        "-r", "--recursive", help="Recursively process directories.", action="store_true"
    )
    parser.add_argument(
        "-c",
        "--color",
        action="append",
        help="List of hex color codes to use for gradient recoloring. Max of 6",
    )
    parser.add_argument(
        "--mono-color",
        default="#acacac",
        help="Hex color code to use for monochrome recoloring. Default is #acacac.",
    )
    parser.add_argument(
        "-o",
        "--output",
        action="store",
        help="The recolored svg files will be stored in this folder. If not defined, the colored svg will replace the original svg",
        type=Path,
    )
    parser.add_argument(
        "--matugen",
        action="store",
        type=Path,
        help="Reads a matugen json containing the generated colors",
    )
    parser.add_argument(
        "--palette",
        action="store",
        choices=["error", "neutral", "neutral_variant", "primary", "secondary", "tertiary"],
        help="Select a matugen palette to use for recoloring",
    )
    args: Args = parser.parse_args()

    svg = SvgRecolorer(args.color, args.mono_color)

    if args.output is not None:
        args.output.mkdir(exist_ok=True, parents=True)

    if args.matugen is not None:
        if args.matugen.is_file() is False:
            error(f"{str(args.matugen)} not a file")

        if args.palette is None:
            error("palette is required when matugen is passed")

        colors = json.loads(args.matugen.read_text())
        palette = colors["palettes"][args.palette]

        args.color = [
            palette["20"],
            palette["40"],
            palette["60"],
            palette["35"],
            palette["35"],
        ]

    for x in args.FILES_OR_DIR:
        if x.exists() is False:
            print(f"warn: {x} does not exist")
            continue

        if x.is_dir():
            handle_folder(svg, args, x)
            continue

        if x.suffix != ".svg":
            print(f"warn: {x} is not a svg file")
            continue

        if x.is_file():
            handle_file(svg, args, x)