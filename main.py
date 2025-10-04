import tkinter as tk
import pyautogui
import time
import threading

stop_typing = False

def start_typing():
    global stop_typing
    stop_typing = False
    text = text_box.get("1.0", tk.END).rstrip("\n")
    try:
        delay_ms = int(delay_entry.get())
    except ValueError:
        delay_ms = 100

    delay = delay_ms / 1000.0

    def type_text():
        for i in range(3, 0, -1):
            start_button.config(text=f"Starting in {i}...")
            time.sleep(1)
        start_button.config(text="Start Typing")
        for char in text:
            if stop_typing:
                break
            pyautogui.write(char, interval=delay)

    threading.Thread(target=type_text, daemon=True).start()

def stop():
    global stop_typing
    stop_typing = True

# Tkinter GUI setup
root = tk.Tk()
root.title("Auto Typer")

# Text box
text_box = tk.Text(root, height=10, width=50)
text_box.pack(pady=10)

# Delay input
delay_label = tk.Label(root, text="Delay between keystrokes (ms):")
delay_label.pack()
delay_entry = tk.Entry(root)
delay_entry.insert(0, "100")
delay_entry.pack(pady=5)

# Start button
start_button = tk.Button(root, text="Start Typing", command=start_typing)
start_button.pack(pady=5)

#Stop Button
stop_button = tk.Button(root, text="Stop Typing", command=stop)
stop_button.pack(pady=5)

root.mainloop()
