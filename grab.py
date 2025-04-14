import mss
import keyboard
import mouse
from PIL import Image, ImageTk, ImageDraw
import datetime
import os
import tkinter as tk
import json
import threading
import subprocess
from pystray import Icon, MenuItem as item, Menu
from screeninfo import get_monitors

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

region1 = config["region1"]
region2 = config["region2"]
tesseract_path = config["tesseract_path"]
output_txt = config["output_text"]
combined_pdf_path = config["combined_pdf"]

img_folder = "captures"
pdf_folder = "pdf_pages"
os.makedirs(img_folder, exist_ok=True)
os.makedirs(pdf_folder, exist_ok=True)

flags = {
    "call_ocr": True
}

def show_popup(image_path=None, message="Capture complete", duration=3000):
    def _popup():
        root = tk.Tk()
        root.withdraw()
        popup = tk.Toplevel(root)
        popup.overrideredirect(True)
        popup.attributes("-topmost", True)
        popup.attributes("-alpha", 0.9)

        width, height = 300, 50
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = screen_width - width - 20
        y = screen_height - height - 60
        popup.geometry(f"{width}x{height}+{x}+{y}")
        popup.configure(bg="black")

        label = tk.Label(popup, text=message, fg="white", bg="black", font=("Segoe UI", 10))
        label.pack(fill="both", expand=True)

        def close():
            if popup.winfo_exists():
                popup.destroy()
            if root.winfo_exists():
                root.destroy()

        popup.after(duration, close)
        root.mainloop()

    threading.Thread(target=_popup, daemon=True).start()

def capture_region(left, top, width, height):
    with mss.mss() as sct:
        region = {"top": top, "left": left, "width": width, "height": height}
        shot = sct.grab(region)
        return Image.frombytes("RGB", shot.size, shot.rgb)

def capture_and_save_image(image, name):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"{name}_{timestamp}.png"
    image_path = os.path.join(img_folder, filename)
    pdf_path = os.path.join(pdf_folder, filename.replace(".png", ".pdf"))
    image.save(image_path)
    show_popup(image_path, f"🖼️ Captured: {filename}")

    if flags["call_ocr"]:
        subprocess.Popen([
            "python", "andread.py", image_path,
            "--text", output_txt,
            "--pdf", pdf_path,
            "--combined", combined_pdf_path,
            "--tesseract", tesseract_path
        ])

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
        capture_and_save_image(cropped, "drag")

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    root.mainloop()

def hotkey_loop():
    def region1_capture():
        x, y, w, h = region1
        image = capture_region(x, y, w, h)
        capture_and_save_image(image, "pos1")

    def region2_capture():
        x, y, w, h = region2
        image = capture_region(x, y, w, h)
        capture_and_save_image(image, "pos2")

    def drag_capture():
        frozen_screen_selector()

    keyboard.add_hotkey("ctrl+alt+1", region1_capture)
    keyboard.add_hotkey("ctrl+alt+2", region2_capture)
    keyboard.add_hotkey("ctrl+alt+3", drag_capture)
    keyboard.wait()

def toggle_flag(flag):
    flags[flag] = not flags[flag]

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
        item("Enable OCR", lambda: toggle_flag("call_ocr"), checked=lambda item: flags["call_ocr"]),
        item("Quit", on_quit)
    )

    icon = Icon("Grab", icon_image, "Grab", menu)
    threading.Thread(target=hotkey_loop, daemon=True).start()
    icon.run()

if __name__ == "__main__":
    create_tray_icon()
