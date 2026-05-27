import pytesseract
from PIL import Image


def extract_invoice_text(image_path: str):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text