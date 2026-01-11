# mono color acacac
import argparse
import json
import sys

from pathlib import Path
from colorama import Fore, Style
from svgtheme.svg import SvgRecolorer
from xdg_base_dirs import xdg_config_home

CONFIG = xdg_config_home() / "svgtheme" / "config.json"

class Args:
    FILES_OR_DIR: list[Path]
    mono_color: str
    color: list[str]
    recursive: bool
    matugen: Path
    output: Path
    palette: str


def error(*msg, exit_code=1):
    print(f"{Fore.RED}{Style.BRIGHT}error:{Style.RESET_ALL}", *msg)
    sys.exit(exit_code)

def warn(*msg):
    print(f"{Fore.LIGHTRED_EX}warn:{Style.RESET_ALL}", *msg)

def handle_folder(svg, args: Args, folder):
    for file, cnt in svg.process_directory(folder, recursive=args.recursive):
        if args.output:
            (args.output / file.relative_to(folder)).write_text(cnt)
        else:
            file.write_text(cnt)


def handle_file(svg, args: Args, file):
    xml = svg.process_file(file)

    if args.output:
        (args.output / file).write_text(xml)
    else:
        file.write_text(xml)

def load_conf() -> list[str]:
    if CONFIG.exists() is False:
        return []
    
    conf: list[str] = json.loads(CONFIG.read_text())
    if isinstance(conf, list) is False:
        error("The config should contain only a list of strings")

    sanitized_conf = []
    for x in conf:
        if isinstance(x, str) is False:
            error(f"skipping {x} since it's not a string")
        
        if x.startswith("#") is False:
            error(f"invalid hex color: {x}")
        
        sanitized_conf.append(x)
    
    return conf

def run():
    parser = argparse.ArgumentParser(
        "svgtheme",
        description="Recolors svg icons with the provided colors.",
        epilog="You can define colors in ~/.config/svgtheme/config.json, just define a list and put some hex colors",
    )

    parser.add_argument(
        "FILES_OR_DIR",
        nargs="+",
        type=Path,
        help="SVG file or directory containing SVG files to recolor.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="Recursively process directories.",
        action="store_true",
    )
    parser.add_argument(
        "-c",
        "--color",
        action="append",
        default=[],
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
        help="A path to a folder where the svg files will be stored, it will be created if the folder doesn't exist. If not defined, the colored svg will replace the original svg",
        type=Path,
    )
    parser.add_argument(
        "--from-matugen-json",
        action="store",
        dest="matugen",
        type=Path,
        help="Reads a matugen json containing the generated colors",
    )
    parser.add_argument(
        "--palette",
        action="store",
        choices=[
            "error",
            "neutral",
            "neutral_variant",
            "primary",
            "secondary",
            "tertiary",
        ],
        help="Select a matugen palette to use for recoloring",
    )
    args: Args = parser.parse_args()
    conf = load_conf()

    svg = SvgRecolorer(args.color, args.mono_color)

    if args.output is not None:
        args.output.mkdir(exist_ok=True, parents=True)

    if len(args.color) == 0 and len(conf) == 0:
        error("provide at least one color")
    
    args.color.extend(conf)

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

    args.output.mkdir(parents=True, exist_ok=True)

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
