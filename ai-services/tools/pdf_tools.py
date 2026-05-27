import pytesseract
from PIL import Image


def extract_invoice_data(file_path):

    image = Image.open(file_path)

    text = pytesseract.image_to_string(image)

    return {
        "raw_text": text
    }