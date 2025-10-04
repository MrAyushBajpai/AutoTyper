import tkinter as tk
import pyautogui
import time
import threading
import keyboard
import random

# --- Global Variables ---
stop_typing = False
key_listeners = {}

# --- Functions ---

def start_typing():
    global stop_typing
    stop_typing = False
    text = text_box.get("1.0", tk.END).rstrip("\n")
    
    try:
        delay_ms = int(delay_entry.get())
    except ValueError:
        delay_ms = 100
    delay = delay_ms / 1000.0

    try:
        rand_min_ms = int(rand_min_entry.get())
        rand_max_ms = int(rand_max_entry.get())
    except ValueError:
        rand_min_ms, rand_max_ms = 0, 0
    rand_min, rand_max = rand_min_ms / 1000.0, rand_max_ms / 1000.0

    try:
        word_min_ms = int(word_min_entry.get())
        word_max_ms = int(word_max_entry.get())
    except ValueError:
        word_min_ms, word_max_ms = 200, 500
    word_min, word_max = word_min_ms / 1000.0, word_max_ms / 1000.0

    if not text:
        info_label.config(text="Text box is empty!")
        return

    # Thread-safe countdown using Tkinter's after
    def countdown(seconds):
        if seconds > 0:
            start_button.config(text=f"Starting in {seconds}...")
            root.after(1000, countdown, seconds - 1)
        else:
            start_button.config(text="Start Typing")
            threading.Thread(target=type_text, args=(text, delay, rand_min, rand_max, word_min, word_max), daemon=True).start()

    countdown(3)

def type_text(text, delay, rand_min, rand_max, word_min, word_max):
    global stop_typing
    words = text.split(" ")
    for i, word in enumerate(words):
        if stop_typing:
            break
        for char in word:
            if stop_typing:
                break
            actual_delay = delay + random.uniform(rand_min, rand_max)
            actual_delay = max(0, actual_delay)
            pyautogui.write(char, interval=actual_delay)
        if i < len(words) - 1:  # Only add space and word delay if not last word
            pyautogui.write(" ")
            word_delay = random.uniform(word_min, word_max)
            time.sleep(word_delay)
    info_label.config(text="Typing finished" if not stop_typing else "Typing stopped")

def stop():
    global stop_typing
    stop_typing = True
    info_label.config(text="Stopped typing")

def remove_focus(event):
    widget = event.widget
    if widget not in (text_box, delay_entry, rand_min_entry, rand_max_entry, word_min_entry, word_max_entry):
        root.focus_set()

# --- Hotkey Functions ---

def set_start_key():
    wait_for_key("start")

def set_stop_key():
    wait_for_key("stop")

def wait_for_key(action):
    root.focus_set()
    info_label.config(text=f"Press a key to set as {action} hotkey...")

    def assign_key(event):
        key = event.name
        if action == "start":
            set_hotkey("start", key, start_typing)
            start_key_label.config(text=f"Start Key: {key.upper()}")
        else:
            set_hotkey("stop", key, stop)
            stop_key_label.config(text=f"Stop Key: {key.upper()}")
        info_label.config(text=f"{action.capitalize()} key set to: {key.upper()}")
        keyboard.unhook(assign_key)

    keyboard.hook(assign_key)

def set_hotkey(name, key, func):
    global key_listeners
    if name in key_listeners:
        keyboard.remove_hotkey(key_listeners[name])
    listener = keyboard.add_hotkey(key, func)
    key_listeners[name] = listener

# --- Tkinter GUI setup ---
root = tk.Tk()
root.title("Auto Typer")

root.bind("<Button-1>", remove_focus)

text_box = tk.Text(root, height=10, width=50)
text_box.pack(pady=10)

delay_label = tk.Label(root, text="Base delay between keystrokes (ms):")
delay_label.pack()
delay_entry = tk.Entry(root)
delay_entry.insert(0, "100")
delay_entry.pack(pady=5)

rand_delay_label = tk.Label(root, text="Random delay range per keystroke (ms, min-max):")
rand_delay_label.pack()
rand_frame = tk.Frame(root)
rand_frame.pack(pady=5)
rand_min_entry = tk.Entry(rand_frame, width=5)
rand_min_entry.insert(0, "0")
rand_min_entry.pack(side=tk.LEFT, padx=(0,5))
rand_max_entry = tk.Entry(rand_frame, width=5)
rand_max_entry.insert(0, "0")
rand_max_entry.pack(side=tk.LEFT)

word_delay_label = tk.Label(root, text="Word delay range (ms, min-max):")
word_delay_label.pack()
word_frame = tk.Frame(root)
word_frame.pack(pady=5)
word_min_entry = tk.Entry(word_frame, width=5)
word_min_entry.insert(0, "0")
word_min_entry.pack(side=tk.LEFT, padx=(0,5))
word_max_entry = tk.Entry(word_frame, width=5)
word_max_entry.insert(0, "0")
word_max_entry.pack(side=tk.LEFT)

start_button = tk.Button(root, text="Start Typing", command=start_typing)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Stop", command=stop)
stop_button.pack(pady=5)

start_key_label = tk.Label(root, text="Start Key: Not set")
start_key_label.pack()
set_start_button = tk.Button(root, text="Set Start Key", command=set_start_key)
set_start_button.pack(pady=2)

stop_key_label = tk.Label(root, text="Stop Key: Not set")
stop_key_label.pack()
set_stop_button = tk.Button(root, text="Set Stop Key", command=set_stop_key)
set_stop_button.pack(pady=2)

info_label = tk.Label(root, text="")
info_label.pack(pady=10)

pyautogui.FAILSAFE = True

root.mainloop()
