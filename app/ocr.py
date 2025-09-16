import cv2
import pathlib
from PIL import Image
import pytesseract

BASE_DIR = pathlib.Path(__file__).parent
IMG_DIR = BASE_DIR / "images"
img_path = IMG_DIR / "images.jpeg"

def preprocess_image(img_path):
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not read image at {img_path}")

    # Resize (scale up for better OCR)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    # Binarization
    _, img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Noise removal
    img = cv2.medianBlur(img, 3)

    return Image.fromarray(img)

processed_img = preprocess_image(img_path)

custom_config = r'--oem 3 --psm 6'
preds = pytesseract.image_to_string(processed_img, lang="eng", config=custom_config)
predictions = [x.strip() for x in preds.split("\n") if x.strip()]

print(predictions)
