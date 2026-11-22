#!/usr/bin/env python3
"""Generate GNOME-friendly rounded hicolor PNG icons from the upstream 64x64 icon."""

import os
import sys
from PIL import Image, ImageDraw, ImageFilter


def build_base_icon(src_path: str, size: int = 512) -> Image.Image:
    src = Image.open(src_path).convert("RGBA")

    # Reserve ~8% transparent margin on each side so the icon matches GNOME HIG sizing.
    margin = int(round(size * 0.08))
    inner = size - 2 * margin
    radius = int(round(inner * 0.22))

    # Upscale the source artwork into the inner squircle area.
    art = src.resize((inner, inner), Image.Resampling.LANCZOS)

    # Anti-aliased rounded rectangle mask.
    mask = Image.new("L", (inner, inner), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle((0, 0, inner - 1, inner - 1), radius=radius, fill=255)

    # Subtle soft drop shadow behind the tile.
    shadow_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw_shadow = ImageDraw.Draw(shadow_layer)
    shadow_offset = max(2, int(round(size * 0.015)))
    draw_shadow.rounded_rectangle(
        (
            margin,
            margin + shadow_offset,
            margin + inner - 1,
            margin + inner - 1 + shadow_offset,
        ),
        radius=radius,
        fill=(0, 0, 0, 85),
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=size * 0.02))

    # Composite the rounded tile onto the transparent canvas.
    tile = Image.new("RGBA", (inner, inner), (0, 0, 0, 0))
    tile.paste(art, (0, 0), mask)

    # Subtle 1px-scaled inner border so the bright yellow edge reads cleanly on light themes.
    border_overlay = Image.new("RGBA", (inner, inner), (0, 0, 0, 0))
    draw_border = ImageDraw.Draw(border_overlay)
    stroke = max(2, int(round(size * 0.008)))
    draw_border.rounded_rectangle(
        (0, 0, inner - 1, inner - 1),
        radius=radius,
        outline=(180, 155, 20, 140),
        width=stroke,
    )
    tile = Image.alpha_composite(tile, border_overlay)

    canvas = shadow_layer
    canvas.paste(tile, (margin, margin), tile)
    return canvas


def main() -> int:
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <src_icon.png> <hicolor_root>", file=sys.stderr)
        return 1

    src_path, hicolor_root = sys.argv[1], sys.argv[2]
    base = build_base_icon(src_path, size=512)

    for px in (48, 64, 128, 256):
        out_dir = os.path.join(hicolor_root, f"{px}x{px}", "apps")
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, "numberrace.png")
        resized = base.resize((px, px), Image.Resampling.LANCZOS)
        resized.save(out_path, format="PNG", optimize=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
