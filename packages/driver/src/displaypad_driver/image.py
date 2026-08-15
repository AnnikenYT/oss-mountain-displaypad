"""Image helpers for DisplayPad.

Provides utilities to convert, rotate, slice, and normalize image/GIF data for sending to the device.
"""

from typing import List, Tuple, Optional, Dict, Union
from PIL import Image, ImageDraw, ImageFont
import os

from .protocol import ICON_SIZE, KEYS_PER_ROW, NUM_KEYS


def _to_pil_image(image_input: Union[str, Image.Image]) -> Image.Image:
    if isinstance(image_input, Image.Image):
        return image_input.copy()
    return Image.open(image_input)


def image_to_bgr102(image_input: Union[str, Image.Image], rotation: int = 0) -> bytes:
    """Convert an image (file path or PIL Image) to 102x102 raw BGR bytes."""
    img = _to_pil_image(image_input).convert("RGB").resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
    if rotation:
        img = img.rotate(-rotation, expand=False)  # PIL rotates CCW, hardware wants CW
    r, g, b = img.split()
    return Image.merge("RGB", (b, g, r)).tobytes()


def split_image_to_tiles(image_input: Union[str, Image.Image], rotation: int = 0) -> List[bytes]:
    """Split a full panel image (612x204 nominal grid) into 12 BGR102 tile byte payloads."""
    grid_w = ICON_SIZE * KEYS_PER_ROW
    grid_h = ICON_SIZE * (NUM_KEYS // KEYS_PER_ROW)
    img = _to_pil_image(image_input).convert("RGB").resize((grid_w, grid_h), Image.LANCZOS)

    tiles = []
    for idx in range(NUM_KEYS):
        row = idx // KEYS_PER_ROW
        col = idx % KEYS_PER_ROW
        x, y = col * ICON_SIZE, row * ICON_SIZE
        tile = img.crop((x, y, x + ICON_SIZE, y + ICON_SIZE))
        if rotation:
            tile = tile.rotate(-rotation, expand=False)
        r, g, b = tile.split()
        bgr = Image.merge("RGB", (b, g, r)).tobytes()
        tiles.append(bgr)

    return tiles


def load_gif_frames(image_input: Union[str, Image.Image], rotation: int = 0) -> Optional[List[Tuple[bytes, int]]]:
    """Extract frames from an animated GIF.

    Returns:
        List of (bgr_bytes, duration_ms) or None if image is not animated.
    """
    try:
        img = _to_pil_image(image_input)
        if not getattr(img, 'is_animated', False) and getattr(img, 'n_frames', 1) <= 1:
            return None
    except Exception:
        return None

    frames = []
    try:
        for i in range(img.n_frames):
            img.seek(i)
            duration = max(img.info.get('duration', 100), 20)
            frame = img.convert("RGB").resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
            if rotation:
                frame = frame.rotate(-rotation, expand=False)
            r, g, b = frame.split()
            bgr = Image.merge("RGB", (b, g, r)).tobytes()
            frames.append((bgr, duration))
    except EOFError:
        pass

    return frames if len(frames) > 1 else None


def split_gif_to_tiles(image_input: Union[str, Image.Image], rotation: int = 0) -> Optional[Dict[int, List[Tuple[bytes, int]]]]:
    """Split an animated GIF into 12 synchronized tile frame lists.

    Returns:
        {key_idx: [(bgr_bytes, duration_ms), ...]} or None if not animated.
    """
    try:
        img = _to_pil_image(image_input)
        if not getattr(img, 'is_animated', False) and getattr(img, 'n_frames', 1) <= 1:
            return None
    except Exception:
        return None

    grid_w = ICON_SIZE * KEYS_PER_ROW
    grid_h = ICON_SIZE * (NUM_KEYS // KEYS_PER_ROW)
    result = {k: [] for k in range(NUM_KEYS)}
    try:
        for i in range(img.n_frames):
            img.seek(i)
            duration = max(img.info.get('duration', 100), 20)
            frame = img.convert("RGB").resize((grid_w, grid_h), Image.LANCZOS)
            for idx in range(NUM_KEYS):
                row = idx // KEYS_PER_ROW
                col = idx % KEYS_PER_ROW
                x, y = col * ICON_SIZE, row * ICON_SIZE
                tile = frame.crop((x, y, x + ICON_SIZE, y + ICON_SIZE))
                if rotation:
                    tile = tile.rotate(-rotation, expand=False)
                r, g, b = tile.split()
                result[idx].append((Image.merge("RGB", (b, g, r)).tobytes(), duration))
    except EOFError:
        pass

    return result if result[0] and len(result[0]) > 1 else None


def make_label_icon(text: str, out_path: Optional[str] = None) -> Image.Image:
    """Render a short text label centered on a 102x102 tile with dark background and shadow."""
    img = Image.new("RGB", (ICON_SIZE, ICON_SIZE), (28, 28, 36))
    draw = ImageDraw.Draw(img)

    label = (text or "").strip()
    font = ImageFont.load_default()

    for size in (30, 26, 22, 18, 15, 12):
        try:
            for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                      "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"):
                if os.path.exists(p):
                    font = ImageFont.truetype(p, size)
                    break
        except Exception:
            pass

        words = label.split()
        lines, cur = [], ""
        for w in words or [label]:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=font) <= ICON_SIZE - 8 or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        lines = lines[:3]
        line_h = (draw.textbbox((0, 0), "Ag", font=font)[3]) + 2
        if line_h * len(lines) <= ICON_SIZE - 6 and all(
                draw.textlength(ln, font=font) <= ICON_SIZE - 6 for ln in lines):
            break

    total_h = line_h * len(lines)
    y = max(2, (ICON_SIZE - total_h) // 2)
    for ln in lines:
        tw = draw.textlength(ln, font=font)
        x = max(2, (ICON_SIZE - tw) // 2)
        draw.text((x + 1, y + 1), ln, fill=(0, 0, 0), font=font)
        draw.text((x, y), ln, fill=(255, 255, 255), font=font)
        y += line_h

    if out_path:
        img.save(out_path, "PNG")
    return img


def make_folder_icon(base_path: str, label: str, out_path: Optional[str] = None) -> Image.Image:
    """Render label text on top of a folder icon base image."""
    img = Image.open(base_path).convert("RGB").resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
    if label:
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                  "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf"):
            if os.path.exists(p):
                try:
                    font = ImageFont.truetype(p, 16)
                    break
                except Exception:
                    pass
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        x = max(2, (ICON_SIZE - tw) // 2)
        draw.text((x + 1, 5), label, fill=(0, 0, 0), font=font)
        draw.text((x, 4), label, fill=(255, 255, 255), font=font)

    if out_path:
        img.save(out_path, "PNG")
    return img

