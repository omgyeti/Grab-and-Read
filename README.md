# Grab&Read

**Grab&Read** is a hotkey-driven, background OCR utility that captures regions of your screen and extracts text into a readable `.txt` file and a searchable `.pdf`.

It runs quietly in the system tray, listens for **numpad hotkeys**, and works with **multi-monitor setups** using native Windows screen capture.

---

## 🚀 Features

- ✅ **Hotkey capture** via numpad
- ✅ **Multi-monitor** support using `mss`
- ✅ **Frozen screen selector** for drag-to-capture
- ✅ System tray menu with:
  - 📝 Config file editor
  - ✅ OCR toggle
  - 📄 PDF generation toggle
  - 🖼️ Screenshot-only mode when both are off
- ✅ Searchable multi-page PDF builder
- ✅ Screenshot popup with image preview

---

## ⌨️ Hotkeys

| Key        | Action                            |
|------------|-----------------------------------|
| Numpad 1   | Capture **Region 1** from config  |
| Numpad 2   | Capture **Region 2** from config  |
| Numpad 3   | **Click-and-drag** custom region  |
| Tray Menu | Enable/disable features or quit   |

---

## 🛠 Setup

### 1. Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

Make sure you add the Tesseract `tesseract.exe` path to your config.

---

### 2. Install dependencies

```bash
pip install -r requirements.txt


<details>
<summary>📦 requirements.txt contents</summary>

```txt
pyautogui
pillow
keyboard
mouse
pytesseract
pystray
plyer
PyPDF2
```
</details>

---

### 3. Create a `config.json`

```json
{
  "tesseract_path": "C:/Path/To/tesseract.exe",
  "region1": [50, 250, 3150, 1050],
  "region2": [946, 298, 1550, 972],
  "output_text": "ocr_output.txt",
  "combined_pdf": "ocr_combined.pdf"
}
```

You can customize the capture regions or output paths here.

---

## ▶️ Running the Tool

### 🖥️ Development Mode (with terminal):

```bash
python grab_and_read.py
```

### 🔕 Silent Background Mode (no terminal):

1. Rename your script:
   ```
   grab_and_read.pyw
   ```

2. Run it with:
   ```
   pythonw grab_and_read.pyw
   ```

3. The app will appear in your **system tray**. It will:
   - Listen for numpad hotkeys
   - Run OCR silently
   - Notify you when output is saved

---

## 📁 Output Files

| File/Folder       | Purpose                                |
|-------------------|----------------------------------------|
| `captures/`       | Screenshot images                      |
| `pdf_pages/`      | Temporary single-page OCR PDFs         |
| `ocr_output.txt`  | Plain text extracted from captures     |
| `ocr_combined.pdf`| Searchable multi-page OCR PDF result   |

---

## 📝 License

MIT – see [LICENSE](LICENSE) for full legal terms.

> This project is open source and totally customizable.  
> You may use, modify, and redistribute it freely.

---

**Grab&Read** was built for makers, testers, engineers, and techs who need quick, repeatable OCR from screens and processes — without interrupting workflow.
