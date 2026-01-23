import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageChops
from svgpathtools import parse_path


def create_rainbow_gradient_image(width=1024, height=1024):
    """
    Fast vertical HSV rainbow gradient from top to bottom.
    """
    # Hue varies vertically
    hue = np.linspace(0.0, 1.0, height, endpoint=False)[:, np.newaxis]
    hue = np.repeat(hue, width, axis=1)

    sat = np.ones_like(hue)
    val = np.ones_like(hue)

    # HSV to RGB (vectorized)
    i = np.floor(hue * 6).astype(int)
    f = hue * 6 - i
    p = val * (1 - sat)
    q = val * (1 - f * sat)
    t = val * (1 - (1 - f) * sat)

    i = i % 6
    
    r = np.choose(i, [val, q, p, p, t, val])
    g = np.choose(i, [t, val, val, q, p, p])
    b = np.choose(i, [p, p, t, val, val, q])

    img = np.stack([r, g, b], axis=2)
    img = (img * 255).astype(np.uint8)

    return Image.fromarray(img, mode="RGB")


def get_icon_mask(icon_path, width=1024, height=1024, curve_steps=20):
    """
    Rasterize SVG paths into a square mask and center it in the output.
    """
    # Final full-size mask
    final_mask = Image.new("1", (width, height), 0)

    # Square mask size
    mask_size = min(width, height)
    square_mask = Image.new("1", (mask_size, mask_size), 0)

    tree = ET.parse(icon_path)
    root = tree.getroot()

    viewbox = root.get("viewBox", "0 0 100 100").split()
    vb_x, vb_y, vb_w, vb_h = map(float, viewbox)

    # Uniform scale to preserve aspect ratio
    scale = mask_size / max(vb_w, vb_h)

    ns = {"svg": "http://www.w3.org/2000/svg"}

    for path_elem in root.findall(".//svg:path", ns):
        d = path_elem.get("d")
        if not d:
            continue

        path = parse_path(d)

        for subpath in path.continuous_subpaths():
            polygon = []

            for segment in subpath:
                for t in np.linspace(0, 1, curve_steps, endpoint=False):
                    pt = segment.point(t)
                    polygon.append(
                        (
                            (pt.real - vb_x) * scale,
                            (pt.imag - vb_y) * scale,
                        )
                    )

            end = subpath[-1].end
            polygon.append(
                (
                    (end.real - vb_x) * scale,
                    (end.imag - vb_y) * scale,
                )
            )

            if len(polygon) < 3:
                continue

            temp = Image.new("1", (mask_size, mask_size), 0)
            ImageDraw.Draw(temp).polygon(polygon, fill=1)
            square_mask = ImageChops.logical_xor(square_mask, temp)

        # Compute bounding box of actual mask content
    bbox = square_mask.getbbox()
    if bbox is None:
        return final_mask.convert("L")

    bbox_left, bbox_top, bbox_right, bbox_bottom = bbox
    content_width = bbox_right - bbox_left
    content_height = bbox_bottom - bbox_top

    # Target center of output image
    target_cx = width // 2
    target_cy = height // 2

    # Current center of mask content
    content_cx = bbox_left + content_width // 2
    content_cy = bbox_top + content_height // 2

    # Offset so that content center aligns with output center
    offset_x = target_cx - content_cx
    offset_y = target_cy - content_cy

    final_mask.paste(square_mask, (offset_x, offset_y))


    return final_mask.convert("L")




def apply_mask(gradient_img, mask_img):
    """
    Apply mask as alpha channel.
    """
    result = gradient_img.convert("RGBA")
    result.putalpha(mask_img)
    return result


if __name__ == "__main__":
    icon_path = Path(__file__).parent / "icon_outline.svg"

    print("Creating rainbow gradient...")
    gradient = create_rainbow_gradient_image(1024, 1024)

    print("Creating mask from icon...")
    mask = get_icon_mask(icon_path, 1024, 1024)

    print("Applying mask...")
    result = apply_mask(gradient, mask)

    output_path = Path(__file__).parent / "icon.png"
    result.save(output_path)

    print(f"Rendered PNG saved to: {output_path}")
