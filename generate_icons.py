#!/usr/bin/env python3
"""生成 PWA 图标 PNG"""
from PIL import Image, ImageDraw, ImageFont
import os

BASE = r"D:\PROJECTALL\MaoGai"
ACCENT = (107, 140, 107)


def make_icon(size, text):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = int(size * 0.1875)
    draw.rounded_rectangle((0, 0, size, size), radius=radius, fill=ACCENT)

    font_size = int(size * 0.51)
    try:
        font = ImageFont.truetype("msyh.ttc", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("simhei.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size - text_w) / 2
    y = (size - text_h) / 2 - text_h * 0.08
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))

    return img


for s in [192, 512]:
    img = make_icon(s, "背")
    img.save(os.path.join(BASE, f"icon-{s}.png"), "PNG")
    print(f"generated icon-{s}.png")
