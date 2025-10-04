import tkinter as tk
import pyautogui
import time
import threading

def start_typing():
    text = text_box.get("1.0", tk.END).rstrip("\n")
    delay = 0.1

    def type_text():
        time.sleep(3)
        for char in text:
            pyautogui.write(char, interval=delay)

    threading.Thread(target=type_text).start()

# Tkinter GUI setup
root = tk.Tk()
root.title("Auto Typer")

# Text box
text_box = tk.Text(root, height=10, width=50)
text_box.pack(pady=10)

# Start button
start_button = tk.Button(root, text="Start Typing", command=start_typing)
start_button.pack(pady=5)

root.mainloop()