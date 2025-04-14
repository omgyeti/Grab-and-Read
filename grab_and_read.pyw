import mss
import keyboard
import mouse
from PIL import Image, ImageTk, ImageDraw
import pytesseract
import datetime
import os
import tkinter as tk
import json
import threading
from PyPDF2 import PdfMerger
from pystray import Icon, MenuItem as item, Menu
import subprocess
from screeninfo import get_monitors

# Load Config
with open("config.json", "r") as f:
    config = json.load(f)

pytesseract.pytesseract.tesseract_cmd = config["tesseract_path"]
output_txt = config["output_text"]
combined_pdf_path = config["combined_pdf"]
region1 = config["region1"]
region2 = config["region2"]

img_folder = "captures"
pdf_folder = "pdf_pages"
os.makedirs(img_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)

flags = {"ocr": True, "pdf": True}

def toggle_flag(flag):
    flags[flag] = not flags[flag]

def show_popup(image_path=None, message="OCR Complete", duration=3000):
    def _popup():
        win = tk.Tk()
        win.withdraw()
        popup = tk.Toplevel(win)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.attributes("-alpha", 0.9)
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        popup_width = 420
        popup_height = 260
        x = screen_width - popup_width - 20
        y = screen_height - popup_height - 60
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup.configure(bg="black")
        canvas = tk.Canvas(popup, width=popup_width, height=popup_height, bg="black", highlightthickness=0)
        canvas.pack()
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path).resize((popup_width, 225))
            tk_img = ImageTk.PhotoImage(img)
            canvas.create_image(0, 0, anchor="nw", image=tk_img)
            popup.tk_img = tk_img
        canvas.create_text(popup_width // 2, popup_height - 20, text=message, fill="white", font=("Segoe UI", 10))
        def on_enter(_): popup.attributes("-alpha", 0.4)
        def on_leave(_): popup.attributes("-alpha", 0.9)
        def on_click(_): popup.destroy(); win.destroy()
        popup.bind("<Enter>", on_enter)
        popup.bind("<Leave>", on_leave)
        popup.bind("<Button-1>", on_click)
        canvas.bind("<Button-1>", on_click)
        popup.after(duration, lambda: (popup.destroy(), win.destroy()))
        win.mainloop()
    threading.Thread(target=_popup, daemon=True).start()

def append_pdf_to_combined(new_pdf_path):
    merger = PdfMerger()
    if os.path.exists(combined_pdf_path):
        merger.append(combined_pdf_path)
    merger.append(new_pdf_path)
    merger.write(combined_pdf_path)
    merger.close()

def capture_region(left, top, width, height):
    with mss.mss() as sct:
        region = {"top": top, "left": left, "width": width, "height": height}
        shot = sct.grab(region)
        return Image.frombytes("RGB", shot.size, shot.rgb)

def capture_and_save_ocr_image(image, name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{name}_{timestamp}"
    image_path = os.path.join(img_folder, f"{base_filename}.png")
    pdf_path = os.path.join(pdf_folder, f"{base_filename}.pdf")
    image.save(image_path)
    if flags["ocr"]:
        text = pytesseract.image_to_string(image)
        with open(output_txt, "a", encoding='utf-8') as f:
            f.write(f"\n\n[{timestamp}] - {name.upper()} REGION\n")
            f.write(f"(Image: {image_path})\n")
            f.write(text.strip())
            f.write("\n" + "=" * 60)
    if flags["pdf"]:
        pdf_bytes = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
        with open(pdf_path, "wb") as f:
            f.write(pdf_bytes)
        append_pdf_to_combined(pdf_path)
    show_popup(image_path, f"OCR complete: {name}")

def frozen_screen_selector():
    monitors = get_monitors()
    min_x = min(m.x for m in monitors)
    min_y = min(m.y for m in monitors)
    max_x = max(m.x + m.width for m in monitors)
    max_y = max(m.y + m.height for m in monitors)
    width = max_x - min_x
    height = max_y - min_y
    screenshot = capture_region(min_x, min_y, width, height)
    root = tk.Tk()
    root.withdraw()
    top = tk.Toplevel(root)
    top.geometry(f"{width}x{height}+{min_x}+{min_y}")
    top.attributes('-topmost', True)
    top.attributes('-alpha', 0.95)
    top.overrideredirect(True)
    canvas = tk.Canvas(top, cursor="cross")
    canvas.pack(fill="both", expand=True)
    img = ImageTk.PhotoImage(screenshot)
    canvas.bg_image = img
    canvas.create_image(0, 0, image=img, anchor="nw")
    rect = None
    start_x = start_y = 0
    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)
    def on_mouse_drag(event):
        canvas.coords(rect, start_x, start_y, event.x, event.y)
    def on_mouse_up(event):
        end_x, end_y = event.x, event.y
        root.quit()
        root.destroy()
        left = min(start_x, end_x)
        top = min(start_y, end_y)
        right = max(start_x, end_x)
        bottom = max(start_y, end_y)
        cropped = screenshot.crop((left, top, right, bottom))
        capture_and_save_ocr_image(cropped, "drag")
    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    root.mainloop()

def hotkey_loop():
    SCAN_NUM1 = 79
    SCAN_NUM2 = 80
    SCAN_NUM3 = 81
    while True:
        try:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                sc = event.scan_code
                if sc == SCAN_NUM1:
                    x, y, w, h = region1
                    image = capture_region(x, y, w, h)
                    capture_and_save_ocr_image(image, "pos1")
                elif sc == SCAN_NUM2:
                    x, y, w, h = region2
                    image = capture_region(x, y, w, h)
                    capture_and_save_ocr_image(image, "pos2")
                elif sc == SCAN_NUM3:
                    frozen_screen_selector()
        except KeyboardInterrupt:
            break

def create_tray_icon():
    icon_image = Image.new("RGB", (64, 64), (30, 30, 30))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle((20, 20, 44, 44), fill="white")
    def on_quit(icon, item):
        icon.stop()
        os._exit(0)
    def edit_config(_=None):
        subprocess.Popen(["notepad.exe", os.path.abspath("config.json")])
    menu = Menu(
        item("Edit Config", edit_config),
        item("Enable OCR", lambda: toggle_flag("ocr"), checked=lambda item: flags["ocr"]),
        item("Enable PDF", lambda: toggle_flag("pdf"), checked=lambda item: flags["pdf"]),
        item("Quit", on_quit)
    )
    icon = Icon("Grab&Read", icon_image, "Grab&Read OCR", menu)
    threading.Thread(target=hotkey_loop, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    create_tray_icon()
