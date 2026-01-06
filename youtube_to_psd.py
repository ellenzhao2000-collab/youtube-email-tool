import os
import re
import subprocess
import requests
from io import BytesIO
from PIL import Image
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer, TypeLayer

def extract_video_id(youtube_url):
    patterns = [r"v=([^&]+)", r"youtu.be/([^?]+)"]
    for p in patterns:
        m = re.search(p, youtube_url)
        if m:
            return m.group(1)
    raise ValueError("Invalid YouTube URL")

def download_thumbnail(video_id):
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
    ]
    for url in urls:
        r = requests.get(url)
        if r.status_code == 200:
            return Image.open(BytesIO(r.content)).convert("RGB")
    raise RuntimeError("No thumbnail found")

def capture_frame(youtube_url, timestamp, out_path):
    subprocess.run([
        "ffmpeg", "-y",
        "-ss", timestamp,
        "-i", youtube_url,
        "-frames:v", "1",
        out_path
    ], check=True)

def insert_image_above_dark(psd, image):
    dark = next(l for l in psd.descendants() if l.name == "Dark")
    new_layer = PixelLayer.from_image(psd, image, name="Video Image")
    parent = dark.parent
    parent.layers.insert(parent.layers.index(dark), new_layer)

def update_headline(psd, text):
    layer = next(
        l for l in psd.descendants()
        if isinstance(l, TypeLayer) and l.name == "Headline"
    )
    layer.text = text

def update_color_block(psd, hex_color):
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
    layer = next(l for l in psd.descendants() if l.name == "Color Block")
    layer.fill_color = (*rgb, 255)

def toggle_brand(psd, mode):
    yt = next(l for l in psd.descendants() if l.name == "YouTube")
    gen = next(l for l in psd.descendants() if l.name == "Generic")
    yt.visible = mode == "youtube"
    gen.visible = mode != "youtube"

def export_jpg(psd, output_path):
    composite = psd.composite()
    composite.save(output_path, "JPEG", quality=95, subsampling=0)

def generate_email_image(
    psd_path,
    youtube_url,
    output_jpg,
    headline_text,
    color_hex,
    branding,
    still_timestamp=None
):
    psd = PSDImage.open(psd_path)
    video_id = extract_video_id(youtube_url)

    if still_timestamp:
        temp = "_frame.jpg"
        capture_frame(youtube_url, still_timestamp, temp)
        image = Image.open(temp).convert("RGB")
        os.remove(temp)
    else:
        image = download_thumbnail(video_id)

    insert_image_above_dark(psd, image)
    update_headline(psd, headline_text)
    update_color_block(psd, color_hex)
    toggle_brand(psd, branding)
    export_jpg(psd, output_jpg)
