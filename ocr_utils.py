import fitz
import cv2, numpy as np
from PIL import Image
from io import BytesIO

def render_first_page(pdf_bytes: bytes) -> Image.Image:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page = doc.load_page(0)
    pix  = page.get_pixmap(dpi=360)
    img  = Image.open(BytesIO(pix.tobytes("png")))
    doc.close()
    return img

def deskew_pil(pil_img: Image.Image) -> Image.Image:
    img = np.array(pil_img.convert("L"))
    thr = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(thr > 0))
    if coords.size == 0:
        return pil_img
    angle = cv2.minAreaRect(coords)[-1]
    angle = -(90 + angle) if angle < -45 else -angle
    (h, w) = img.shape
    M = cv2.getRotationMatrix2D((w//2, h//2), angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return Image.fromarray(rotated)
