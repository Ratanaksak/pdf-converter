from flask import Flask, render_template, request, send_file
import os
from pdf2docx import Converter
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from docx import Document
import pytesseract
from pdf2image import convert_from_path

app = Flask(__name__)

# Folders
uploads_dir = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(uploads_dir):
    os.makedirs(uploads_dir)
output_path = os.path.join('static', 'output.docx')

# Tesseract OCR path (adjust for your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler-25.07.0\Library\bin"

# Khmer detection
def is_khmer(char):
    return 0x1780 <= ord(char) <= 0x17FF

def contains_khmer(text):
    return any(is_khmer(char) for char in text)

# Detect Khmer pages
def check_khmer_pages(pdf_path):
    khmer_pages = []
    for page_num, page_layout in enumerate(extract_pages(pdf_path), start=1):
        page_text = ""
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                page_text += element.get_text()
        if contains_khmer(page_text):
            khmer_pages.append(page_num)
    return khmer_pages

# Convert PDF → Word (preserve layout)
def convert_pdf_to_word(pdf_file):
    cv = Converter(pdf_file)
    cv.convert(output_path, start=0, end=None)
    cv.close()
    return output_path

# Extract Khmer text using OCR
def extract_khmer_text_from_pdf(pdf_file):
    pages = convert_from_path(pdf_file, dpi=300, poppler_path=POPPLER_PATH)
    khmer_text = ""
    for i, page in enumerate(pages, start=1):
        text = pytesseract.image_to_string(page, lang="khm")
        if text.strip():
            khmer_text += f"📄 Page {i}:\n{text.strip()}\n\n"
    return khmer_text

@app.route('/')
def index():
    return render_template('pdfconverter.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'pdfFile' not in request.files:
        return "No PDF file provided."

    pdf_file = request.files['pdfFile']
    if pdf_file.filename == '':
        return "No selected file."

    pdf_file_path = os.path.join(uploads_dir, pdf_file.filename)
    pdf_file.save(pdf_file_path)

    if pdf_file.filename.endswith('.pdf'):
        # Step 1: Detect Khmer pages
        khmer_pages = check_khmer_pages(pdf_file_path)

        # Step 2: Convert PDF normally (preserve layout, images, tables)
        convert_pdf_to_word(pdf_file_path)

        # Step 3: If Khmer exists, extract OCR text and append at the end
        if khmer_pages:
            ocr_text = extract_khmer_text_from_pdf(pdf_file_path)
            doc = Document(output_path)
            doc.add_page_break()
            doc.add_paragraph("⚠️ Khmer text extracted by OCR (original PDF may have formatting issues):")
            doc.add_paragraph(ocr_text.strip())
            doc.save(output_path)

        os.remove(pdf_file_path)

        if khmer_pages:
            return f"⚠️ PDF contains Khmer characters on pages {khmer_pages}. OCR text added at the end.<br>" \
                   f"✅ <a href='/download'>Download Word Document</a>"
        else:
            return f"✅ Conversion successful! <a href='/download'>Download Word Document</a>"
    else:
        return "Invalid file format. Please upload a PDF file."

@app.route('/download')
def download():
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
