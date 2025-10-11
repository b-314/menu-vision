import cv2
import numpy as np
from PIL import Image
from pydantic import BaseModel
from typing import List, Optional
from app.models import Category, Food
import easyocr
import re

class MenuParser:
    def __init__(self, image: Image.Image):
        self.original_image = image
        self.processed_image = None
        self.text_lines = []

    # ----------------- Image Preprocessing -----------------
    def preprocess_image(self):
        # Convert PIL to OpenCV
        cv_img = np.array(self.original_image.convert("RGB"))[:, :, ::-1].copy()

        # Perspective / skew correction
        cv_img = self.correct_perspective(cv_img)

        # Convert to grayscale
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # Denoise
        gray = cv2.GaussianBlur(gray, (3,3), 0)

        # Adaptive thresholding
        processed = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            35, 11
        )

        self.processed_image = processed
        return processed

    def correct_perspective(self, cv_img):
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return cv_img
        largest = max(contours, key=cv2.contourArea)
        epsilon = 0.02 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            rect = np.zeros((4, 2), dtype="float32")
            s = pts.sum(axis=1)
            rect[0] = pts[np.argmin(s)]
            rect[2] = pts[np.argmax(s)]
            diff = np.diff(pts, axis=1)
            rect[1] = pts[np.argmin(diff)]
            rect[3] = pts[np.argmax(diff)]
            (tl, tr, br, bl) = rect
            widthA = np.linalg.norm(br - bl)
            widthB = np.linalg.norm(tr - tl)
            heightA = np.linalg.norm(tr - br)
            heightB = np.linalg.norm(tl - bl)
            maxWidth = int(max(widthA, widthB))
            maxHeight = int(max(heightA, heightB))
            dst = np.array([[0, 0], [maxWidth-1, 0], [maxWidth-1, maxHeight-1], [0, maxHeight-1]], dtype="float32")
            M = cv2.getPerspectiveTransform(rect, dst)
            warp = cv2.warpPerspective(cv_img, M, (maxWidth, maxHeight))
            return warp
        return cv_img

    # ----------------- Column Detection -----------------
    def split_columns(self):
        if self.processed_image is None:
            self.preprocess_image()
        cv_img = cv2.cvtColor(self.processed_image, cv2.COLOR_GRAY2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, cv_img.shape[0]//2))
        mask = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, vertical_kernel)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        columns = []
        for c in contours:
            x, y, w, h = cv2.boundingRect(c)
            columns.append(cv_img[y:y+h, x:x+w])
        columns = sorted(columns, key=lambda c: c.shape[1])  # left to right
        if not columns:
            columns = [cv_img]
        return columns

    # ----------------- OCR -----------------
    def extract_text(self):
        reader = easyocr.Reader(['en'])
        columns = self.split_columns()
        all_text = []

        for col in columns:
            result = reader.readtext(col)
            # Sort by y-coordinate (top to bottom)
            sorted_result = sorted(result, key=lambda r: r[0][0][1])
            for bbox, text, conf in sorted_result:
                all_text.append(text.strip())

        self.text_lines = all_text
        return "\n".join(all_text)

    # ----------------- Parsing -----------------
    def parse(self) -> List[Category]:
        if not self.text_lines:
            self.extract_text()
        lines = [l for l in self.text_lines if l]

        categories: List[Category] = []
        current_category: Optional[Category] = None

        # Regex to detect food + price (price optional)
        food_pattern = re.compile(r"(?P<name>[A-Za-z0-9\s&',.-]+?)\s*\$?(?P<price>\d+(?:\.\d+)?)?$")

        for line in lines:
            # Detect category (all caps or single words)
            if line.isupper() and len(line.split()) < 4:
                current_category = Category(name=line.title(), items=[])
                categories.append(current_category)
            elif current_category:
                match = food_pattern.match(line)
                if match:
                    name = match.group("name").strip()
                    price = match.group("price")
                    current_category.add_food(Food(name=name, price=float(price) if price else None))

        return categories