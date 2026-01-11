# Svgtheme
Recolors svgs with the provided color scheme.

I just took the svg recoloring part from [here](https://www.reddit.com/r/unixporn/comments/1q6ngwh/oc_auto_svg_icon_recolorer_to_match_every_icon_to/) and refactored it.

## Features
- Recolors all svgs in a directory to match the provided color scheme.
- You can provide an output directory.
- Reads colors from a matugen json file.
- Gets colors from the config file.

## Configuration
Create a config file at `~/.config/svgtheme/config.json` and define an array of colors in it. Example:
```json
[
    "#282c34",
    "#3b4048",
    "#61afef",
    "#98c379",
    "#e06c75",
    "#c678dd",
]```
The colors defined in this file are appended to the colors passed as command-line arguments.

## Usage
```bash
svgtheme -i file_or_directory -o output_directory -c "#ff0000" -c "#00ff00" -c "#0000ff"
```