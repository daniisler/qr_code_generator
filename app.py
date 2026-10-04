import base64
from io import BytesIO
from pathlib import Path
import re

import cairosvg
import qrcode
from flask import Flask, render_template, request, send_file
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

ERROR_CORRECTION_LEVELS = {
    "L": (qrcode.constants.ERROR_CORRECT_L, "Low (7%)"),
    "M": (qrcode.constants.ERROR_CORRECT_M, "Medium (15%)"),
    "Q": (qrcode.constants.ERROR_CORRECT_Q, "Quartile (25%)"),
    "H": (qrcode.constants.ERROR_CORRECT_H, "High (30%)"),
}
BOX_SIZES = {"6", "8", "10", "12", "16"}
BORDERS = {"2", "4", "6", "8"}
COLOR_PATTERN = re.compile(r"^#[0-9a-fA-F]{6}$")
LOGO_TEMPLATES = {
    "dino": "Dino (example)",
    "sparkle": "Sparkle (example)",
    # "leaf": "Leaf (example)",
    "rocket": "Rocket (example)",
}
TEMPLATE_DIR = Path(__file__).parent / "static" / "templates"


def image_from_logo(template_name, uploaded_file):
    if uploaded_file and uploaded_file.filename:
        try:
            return Image.open(uploaded_file).convert("RGBA")
        except (UnidentifiedImageError, OSError):
            raise ValueError("Choose a valid PNG, JPEG, GIF, or WebP image.")

    if template_name in LOGO_TEMPLATES:
        svg_data = (TEMPLATE_DIR / f"{template_name}.svg").read_bytes()
        png_data = cairosvg.svg2png(bytestring=svg_data, output_width=512, output_height=512)
        return Image.open(BytesIO(png_data)).convert("RGBA")

    return None


def make_qr_image(text, correction, foreground, background, box_size, border, logo_template, logo_file):
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECTION_LEVELS[correction][0],
        box_size=int(box_size),
        border=int(border),
    )
    qr.add_data(text)
    qr.make(fit=True)
    image = qr.make_image(fill_color=foreground, back_color=background).convert("RGBA")
    logo = image_from_logo(logo_template, logo_file)

    if logo:
        logo_size = max(32, int(image.width * 0.2))
        logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)
        pad = 12
        logo_background = Image.new(
            "RGBA",
            (logo.width + pad * 2, logo.height + pad * 2),
            background,
        )
        logo_background.alpha_composite(logo, (pad, pad))
        position = (
            (image.width - logo_background.width) // 2,
            (image.height - logo_background.height) // 2,
        )
        image.alpha_composite(logo_background, position)

    return image


def image_as_base64(image):
    image_data = BytesIO()
    image.save(image_data, format="PNG")
    return base64.b64encode(image_data.getvalue()).decode("ascii")


@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    preview_data = None
    text = ""
    correction = "H"
    foreground = "#000000"
    background = "#ffffff"
    box_size = "10"
    border = "4"
    logo_template = ""

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        correction = request.form.get("correction", "H")
        foreground = request.form.get("foreground", "#000000")
        background = request.form.get("background", "#ffffff")
        box_size = request.form.get("box_size", "10")
        border = request.form.get("border", "4")
        logo_template = request.form.get("logo_template", "")
        logo_file = request.files.get("logo_file")

        if not text:
            error = "Enter some text or a URL first."
        elif len(text) > 4096:
            error = "Please keep the text below 4,096 characters."
        elif correction not in ERROR_CORRECTION_LEVELS:
            error = "Choose a valid error correction level."
        elif not COLOR_PATTERN.fullmatch(foreground) or not COLOR_PATTERN.fullmatch(background):
            error = "Choose valid six-digit colors."
        elif box_size not in BOX_SIZES or border not in BORDERS:
            error = "Choose valid image sizing options."
        elif logo_template not in {"", *LOGO_TEMPLATES}:
            error = "Choose a valid logo template."
        else:
            try:
                image = make_qr_image(
                    text,
                    correction,
                    foreground,
                    background,
                    box_size,
                    border,
                    logo_template,
                    logo_file,
                )
                preview_data = image_as_base64(image)
            except ValueError as image_error:
                error = str(image_error)

    return render_template(
        "index.html",
        error=error,
        text=text,
        correction=correction,
        correction_levels=ERROR_CORRECTION_LEVELS,
        foreground=foreground,
        background=background,
        box_size=box_size,
        border=border,
        logo_template=logo_template,
        logo_templates=LOGO_TEMPLATES,
        preview_data=preview_data,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8500, debug=False)
