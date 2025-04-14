import pytesseract
from PIL import Image
from PyPDF2 import PdfMerger
import argparse
import os
import datetime
import sys

parser = argparse.ArgumentParser(description="OCR an image and optionally save text, PDF, and combined PDF.")
parser.add_argument("image_path", help="Path to the image file to OCR")
parser.add_argument("--text", help="Output .txt file to append OCR text")
parser.add_argument("--pdf", help="Path to save single-page searchable PDF")
parser.add_argument("--combined", help="Path to append the single-page PDF into a combined PDF")
parser.add_argument("--tesseract", help="Path to tesseract executable, if not in PATH")

args = parser.parse_args()

if args.tesseract:
    pytesseract.pytesseract.tesseract_cmd = args.tesseract

if not os.path.exists(args.image_path):
    print(f"❌ Image not found: {args.image_path}")
    sys.exit(1)

image = Image.open(args.image_path)
timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
base_name = os.path.basename(args.image_path)

# Perform OCR
text = pytesseract.image_to_string(image)
print("🔍 OCR Result:")
print(text.strip())

# Save text if requested
if args.text:
    with open(args.text, "a", encoding='utf-8') as f:
        f.write(f"\n\n[{timestamp}] - OCR from {base_name}\n")
        f.write(f"(Image: {args.image_path})\n")
        f.write(text.strip())
        f.write("\n" + "="*60)
    print(f"📝 Text appended to {args.text}")

# Save single-page searchable PDF
pdf_path = None
if args.pdf:
    pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
    with open(args.pdf, "wb") as f:
        f.write(pdf_bytes)
    pdf_path = args.pdf
    print(f"📄 PDF saved to {args.pdf}")

# Append to combined PDF
if args.combined and pdf_path:
    try:
        merger = PdfMerger()
        if os.path.exists(args.combined):
            merger.append(args.combined)
        merger.append(pdf_path)
        merger.write(args.combined)
        merger.close()
        print(f"📚 Appended to combined PDF: {args.combined}")
    except PermissionError:
        print(f"⚠️ Cannot append to combined PDF. Is it open in another program?")
