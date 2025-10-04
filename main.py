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
        max_rand_ms = int(rand_delay_entry.get())
    except ValueError:
        max_rand_ms = 0
    max_rand = max_rand_ms / 1000.0  # convert ms to seconds

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
            threading.Thread(target=type_text, args=(text, delay, max_rand), daemon=True).start()

    countdown(3)

def type_text(text, delay, max_rand):
    global stop_typing
    for char in text:
        if stop_typing:
            break
        # Calculate random offset between -max_rand and +max_rand
        actual_delay = delay + random.uniform(-max_rand, max_rand)
        # Ensure delay is never negative
        actual_delay = max(0, actual_delay)
        pyautogui.write(char, interval=actual_delay)
    info_label.config(text="Typing finished" if not stop_typing else "Typing stopped")

def stop():
    global stop_typing
    stop_typing = True
    info_label.config(text="Stopped typing")

def remove_focus(event):
    widget = event.widget
    if widget not in (text_box, delay_entry, rand_delay_entry):
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
    """Safely update a global hotkey listener."""
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

delay_label = tk.Label(root, text="Delay between keystrokes (ms):")
delay_label.pack()
delay_entry = tk.Entry(root)
delay_entry.insert(0, "100")
delay_entry.pack(pady=5)

rand_delay_label = tk.Label(root, text="Max random delay offset (ms, optional):")
rand_delay_label.pack()
rand_delay_entry = tk.Entry(root)
rand_delay_entry.insert(0, "0")
rand_delay_entry.pack(pady=5)

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
