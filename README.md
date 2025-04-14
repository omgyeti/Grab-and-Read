# Grab&Read

**Grab&Read** is a hotkey-driven OCR utility that captures regions of your screen and extracts text into a readable `.txt` file and a searchable `.pdf`.

It runs silently in the **Windows system tray**, listens for **numpad hotkeys**, and shows **native notifications** when actions complete — no terminal needed.

---

## 🚀 Features

- ✅ Trigger screen captures using your **numpad**
- ✅ Frozen-screen selector for drag-and-capture
- ✅ Background process – no terminal window
- ✅ Native system notifications (via `plyer`)
- ✅ System tray icon with exit menu (via `pystray`)
- ✅ Automatically merges OCR into a single PDF
- OCR powered by [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)

---

## ⌨️ Hotkeys

| Key        | Action                             |
|------------|------------------------------------|
| Numpad 1   | Capture fixed region 1             |
| Numpad 2   | Capture fixed region 2             |
| Numpad 3   | Click-and-drag on a frozen screen  |
| Tray Menu | Right-click icon → Quit             |

---

## 🛠 Setup

### 1. Install Tesseract OCR

- [Download Tesseract](https://github.com/tesseract-ocr/tesseract)
- Install and note the path to `tesseract.exe`

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

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
