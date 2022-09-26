#!/usr/bin/env python3

import argparse
import colorsys
import base64
import os
import re
from textwrap import wrap

from PIL import Image


class ThumbnailProcessor:

    filament_color = ""

    thumbnail_size = ""
    new_thumbnail_char_count = 0
    tmp_thumb_name = "tmp_thumb.png"
    tmp_thumb_dir = os.path.dirname(os.path.realpath(__file__))
    tmp_thumb_path = os.path.join(tmp_thumb_dir, tmp_thumb_name)

    def remove_thumbnail_data(self, file: str) -> None:
        with open(file, "r", encoding="utf-8") as fopen:
            data = fopen.readlines()

        thumb_ranges = []
        thumb_range = ()
        for i, x in enumerate(data):
            if x.startswith("; thumbnail begin"):
                thumb_start = i - 1
                thumb_range = (thumb_start,)

            if x.startswith("; thumbnail end"):
                thumb_end = i + 2
                thumb_range += (thumb_end,)

                # append only if thumb_range is valid
                if len(thumb_range) == 2:
                    thumb_ranges.append(thumb_range)

        # remove the thumbnail data from the data list
        # the index at which the first thumbnail began is the starting point
        # the amount of required pop operations is determined by the difference of
        # last thumbnail end index and first thumbnail start index
        pop_cycles = thumb_ranges[len(thumb_ranges) - 1][1] - thumb_ranges[0][0]
        for _ in range(pop_cycles + 1):
            data.pop(thumb_ranges[0][0])

        # open the file again in write-only mode and write the modified content
        with open(file, mode="w", encoding="utf-8") as fopen:
            fopen.writelines(data)

    def extract_thumbnail_image(self, file: str) -> None:
        with open(file, mode="r", encoding="utf-8") as fopen:
            # read content of file and write it into a string
            file_data = fopen.readlines()
            file_data = "".join(str(e) for e in file_data)

            # parse the original thumbnail size
            match = re.search(r"; thumbnail begin (\d+x\d+)", file_data)
            self.thumbnail_size = match.group(1)

            # parse the filament color
            match = re.search(r"; filament_colour = (#[0-9A-Z]+)", file_data)
            self.filament_color = match.group(1)

            # extract the base64 encoded thumbnail data from gcode
            thumb_matches = re.findall(r"; thumbnail begin[;/\+=\w\s]+?; thumbnail end", file_data)
            for match in thumb_matches:
                lines = re.split(r"\r?\n", match.replace('; ', ''))
                data = "".join(lines[1:-1])

            # decode data and create thumbnail
            with open(self.tmp_thumb_path, mode="wb") as tmp:
                tmp.write(base64.b64decode(data.encode()))

    def encode_image(self) -> str:
        with open(self.tmp_thumb_path, mode="rb") as fopen:
            b64 = str(base64.b64encode(fopen.read()))
            b64 = b64.split("'")[1]

        self.new_thumbnail_char_count = len(b64)

        return b64

    def write_thumbnail_metadata(self, file: str, b64: str):
        thumbnail = wrap(b64, 78)
        thumbnail_data = ["\n" ";\n",
                          f"; thumbnail begin {self.thumbnail_size} {self.new_thumbnail_char_count}\n"]

        for line in thumbnail:
            thumbnail_data.append(f"; {line}\n")
        thumbnail_data.append("; thumbnail end")

        with open(file, mode="a", encoding="utf-8") as fopen:
            fopen.writelines(thumbnail_data)

    def _convert_hex_to_hsv(self, hex_color: str) -> tuple:
        if hex_color.startswith("#"):
            hex_color = hex_color.replace("#", "")

        rgb_color = []
        for i in (0, 2, 4):
            rgb_color.append(int(hex_color[i:i + 2], 16))

        red = rgb_color[0] / 255
        green = rgb_color[1] / 255
        blue = rgb_color[2] / 255
        hsv_color = colorsys.rgb_to_hsv(red, green, blue)

        return hsv_color

    def modify_thumbnail(self, rm_bg: bool):
        file = self.tmp_thumb_path
        hex_input = self.filament_color
        hsv_from_hex = self._convert_hex_to_hsv(hex_input)

        # OPEN IMAGE IN HSV MODE
        image = Image.open(file, mode="r").convert(mode="HSV").getdata()

        hsv_data = []
        for pixel in image:
            hue = pixel[0] / 255
            saturation = pixel[1] / 255
            value = pixel[2] / 255

            # replace original hue with new hue value
            if hue > 0:
                hue = hsv_from_hex[0]

            hsv_pixel = (hue, saturation, value)
            hsv_data.append(hsv_pixel)

        # CONVERT HSV DATA TO RGBA DATA
        rgba_data = []
        for pixel in hsv_data:
            rgb = colorsys.hsv_to_rgb(pixel[0], pixel[1], pixel[2])
            red = int(rgb[0] * 255)
            green = int(rgb[1] * 255)
            blue = int(rgb[2] * 255)
            alpha = 255

            # remove all background pixel
            if rm_bg and red == green == blue:
                red, green, blue, alpha = 255, 255, 255, 0

            rgba_pixel = (red, green, blue, alpha)
            rgba_data.append(rgba_pixel)

        # WRITE NEW IMAGE WITH MODIFIED DATA
        new_image = Image.open(file, mode="r").convert(mode="RGBA")
        new_image.putdata(rgba_data)
        new_image.save(file, "PNG")

    def delete_tmp_thumb(self):
        os.remove(self.tmp_thumb_path)


def main(file: str, rm_bg: bool) -> None:

    print(f"Path to gcode: {file}")
    print(f"Remove thumbnail background? {rm_bg}")

    thumbnail = ThumbnailProcessor()

    # extract thumbnail metadata and modify it
    thumbnail.extract_thumbnail_image(file)
    thumbnail.modify_thumbnail(rm_bg)

    # remove the original thumbnail metadata
    thumbnail.remove_thumbnail_data(file)

    # encode updated thumbnail metadata and write
    # the data at the end of the gcode file
    thumbnail.write_thumbnail_metadata(file, thumbnail.encode_image())

    # delete the temporary thumbnail
    thumbnail.delete_tmp_thumb()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prusa Slicer Thumbnail Post Processor")

    parser.add_argument("file", type=str)
    parser.add_argument("-nb", "--nobackground",
                        dest="no_background",
                        action="store_true",
                        help="[optional] - remove thumbnail background")

    args = parser.parse_args()
    no_background = args.no_background

    main(args.file, no_background)
