import docx
from PIL import Image, ImageFilter
import pytesseract

class OCRService:
    def pdf_to_text(self, file_path):
        text = ""
        try:
            import pdfplumber
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text and len(page_text.strip()) > 50:
                        text += page_text + "\n"
            if text.strip():
                return text
        except Exception:
            pass  # Fallback to OCR below

        # Fallback: use pdf2image + pytesseract on every page
        try:
            from pdf2image import convert_from_path
            pages = convert_from_path(file_path, dpi=300)
            for page in pages:
                gray = page.convert("L")
                bw = gray.point(lambda x: 0 if x < 180 else 255, '1')
                sharp = bw.filter(ImageFilter.SHARPEN)
                ocr_text = pytesseract.image_to_string(sharp)
                text += ocr_text + "\n"
        except Exception as e:
            print(f"OCR extraction failed: {e}")
        return text

    def image_to_text(self, file_path):
        img = Image.open(file_path)
        gray = img.convert("L")
        bw = gray.point(lambda x: 0 if x < 180 else 255, '1')
        sharp = bw.filter(ImageFilter.SHARPEN)
        return pytesseract.image_to_string(sharp)

    def word_to_text(self, file_path):
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
