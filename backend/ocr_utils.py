import cv2
import pytesseract

# preprocess the image
def preprocess_img(img_path: str) -> str:
    img = cv2.imread(img_path)

    grayscale = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    grayscale = cv2.threshold(
        grayscale, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(grayscale)

    return text