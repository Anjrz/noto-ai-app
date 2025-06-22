from PIL import Image
import pytesseract
import PyPDF2

class OCRService:
    def image_to_text(self, image_path):
        try:
            return pytesseract.image_to_string(Image.open(image_path))
        except Exception as e:
            return f"OCR Error: {e}"

    def pdf_to_text(self, pdf_path):
        text = ''
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + '\n'
            return text
        except Exception as e:
            return f"PDF Error: {e}"
