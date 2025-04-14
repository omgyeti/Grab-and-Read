import pyautogui
import keyboard
import mouse
from PIL import Image, ImageTk, ImageDraw
import pytesseract
import time
import sys
import datetime
import os
import tkinter as tk
import json
import threading
from PyPDF2 import PdfMerger
from pystray import Icon, MenuItem as item, Menu
from plyer import notification

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

pytesseract.pytesseract.tesseract_cmd = config["tesseract_path"]
output_txt = config["output_text"]
combined_pdf_path = config["combined_pdf"]
region1 = config["region1"]
region2 = config["region2"]

img_folder = "captures"
temp_pdf_folder = "pdf_pages"
os.makedirs(img_folder, exist_ok=True)
os.makedirs(temp_pdf_folder, exist_ok=True)

def notify(title, message, duration=5):
    notification.notify(
        title=title,
        message=message,
        timeout=duration
    )

def append_pdf_to_combined(new_pdf_path):
    merger = PdfMerger()
    if os.path.exists(combined_pdf_path):
        merger.append(combined_pdf_path)
    merger.append(new_pdf_path)
    merger.write(combined_pdf_path)
    merger.close()
    notify("Grab&Read", f"PDF updated: {os.path.basename(new_pdf_path)}")

def capture_and_save_ocr(left, top, width, height, name):
    screen_width, screen_height = pyautogui.size()
    if width <= 0 or height <= 0 or left + width > screen_width or top + height > screen_height:
        notify("Grab&Read", "Invalid region, capture failed.")
        return

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base_filename = f"{name}_{timestamp}"
    image_path = os.path.join(img_folder, f"{base_filename}.png")
    temp_pdf_path = os.path.join(temp_pdf_folder, f"{base_filename}.pdf")

    screenshot = pyautogui.screenshot(region=(left, top, width, height))
    screenshot.save(image_path)

    text = pytesseract.image_to_string(screenshot)

    with open(output_txt, "a", encoding='utf-8') as f:
        f.write(f"\n\n[{timestamp}] - {name.upper()} REGION\n")
        f.write(f"(Image: {image_path})\n")
        f.write(text.strip())
        f.write("\n" + "="*60)

    pdf_bytes = pytesseract.image_to_pdf_or_hocr(screenshot, extension='pdf')
    with open(temp_pdf_path, "wb") as f:
        f.write(pdf_bytes)

    append_pdf_to_combined(temp_pdf_path)
    notify("Grab&Read", f"OCR complete: {name}")

def frozen_screen_selector():
    screenshot = pyautogui.screenshot()
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.attributes('-alpha', 0.95)
    canvas = tk.Canvas(root, cursor="cross")
    canvas.pack(fill="both", expand=True)
    img = ImageTk.PhotoImage(screenshot)
    canvas.create_image(0, 0, image=img, anchor="nw")

    rect = None
    start_x = start_y = 0

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y, outline="red", width=2)

    def on_mouse_drag(event):
        nonlocal rect
        canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_mouse_up(event):
        nonlocal start_x, start_y
        end_x, end_y = event.x, event.y
        root.quit()
        root.destroy()
        left = min(start_x, end_x)
        top = min(start_y, end_y)
        width = abs(end_x - start_x)
        height = abs(end_y - start_y)
        capture_and_save_ocr(left, top, width, height, "drag")

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    root.mainloop()

# Numpad scan codes
SCAN_NUM1 = 79
SCAN_NUM2 = 80
SCAN_NUM3 = 81

def hotkey_loop():
    notify("Grab&Read", "Running in background (tray icon)", 3)
    while True:
        try:
            event = keyboard.read_event()
            if event.event_type == keyboard.KEY_DOWN:
                sc = event.scan_code
                if sc == SCAN_NUM1:
                    capture_and_save_ocr(*region1, "pos1")
                elif sc == SCAN_NUM2:
                    capture_and_save_ocr(*region2, "pos2")
                elif sc == SCAN_NUM3:
                    frozen_screen_selector()
        except KeyboardInterrupt:
            break

def create_tray_icon():
    icon_image = Image.new("RGB", (64, 64), (30, 30, 30))
    draw = ImageDraw.Draw(icon_image)
    draw.rectangle((20, 20, 44, 44), fill="white")

    def on_quit(icon, item):
        notify("Grab&Read", "Shutting down")
        icon.stop()
        os._exit(0)

    menu = Menu(
        item("Quit", on_quit)
    )

    icon = Icon("Grab&Read", icon_image, "Grab&Read OCR", menu)
    threading.Thread(target=hotkey_loop, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    create_tray_icon()
