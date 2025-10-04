import tkinter as tk
import pyautogui
import time
import threading
import keyboard
import random

# --- Global Variables ---
stop_typing = False
is_typing = False  # Flag to check if typing is ongoing
key_listeners = {}

# --- Functions ---

def start_typing():
    global stop_typing, is_typing
    if is_typing:
        info_label.config(text="Already typing!")
        return

    stop_typing = False
    is_typing = True
    text = text_box.get("1.0", tk.END).rstrip("\n")

    # Typing delay
    try:
        delay_ms = int(delay_entry.get())
    except ValueError:
        delay_ms = 100
    delay = delay_ms / 1000.0

    # Random per-character delay
    try:
        rand_min_ms = int(rand_min_entry.get())
        rand_max_ms = int(rand_max_entry.get())
    except ValueError:
        rand_min_ms, rand_max_ms = 0, 0
    rand_min, rand_max = rand_min_ms / 1000.0, rand_max_ms / 1000.0

    # Word delay
    try:
        word_min_ms = int(word_min_entry.get())
        word_max_ms = int(word_max_entry.get())
    except ValueError:
        word_min_ms, word_max_ms = 200, 500
    word_min, word_max = word_min_ms / 1000.0, word_max_ms / 1000.0

    # Startup delay
    try:
        startup_delay_ms = int(startup_delay_entry.get())
        if startup_delay_ms < 0:
            startup_delay_ms = 0
    except ValueError:
        startup_delay_ms = 3000
    startup_delay = startup_delay_ms / 1000.0

    # Typo chance
    try:
        typo_chance = float(typo_entry.get()) / 100.0
        if typo_chance < 0 or typo_chance > 1:
            typo_chance = 0.0
    except ValueError:
        typo_chance = 0.0

    # Typo length range
    try:
        typo_len_min = int(typo_len_min_entry.get())
        typo_len_max = int(typo_len_max_entry.get())
        if typo_len_min < 1: typo_len_min = 1
        if typo_len_max < typo_len_min: typo_len_max = typo_len_min
    except ValueError:
        typo_len_min, typo_len_max = 1, 1

    # Typo correction delay range
    try:
        typo_delay_min_ms = int(typo_delay_min_entry.get())
        typo_delay_max_ms = int(typo_delay_max_entry.get())
        if typo_delay_min_ms < 0: typo_delay_min_ms = 0
        if typo_delay_max_ms < typo_delay_min_ms: typo_delay_max_ms = typo_delay_min_ms
    except ValueError:
        typo_delay_min_ms, typo_delay_max_ms = 50, 50

    if not text:
        info_label.config(text="Text box is empty!")
        is_typing = False
        return

    # Countdown
    def countdown(seconds_remaining):
        if seconds_remaining > 0:
            start_button.config(text=f"Starting in {int(seconds_remaining*1000)}ms...")
            root.after(100, countdown, seconds_remaining - 0.1)
        else:
            start_button.config(text="Start Typing")
            threading.Thread(
                target=type_text,
                args=(text, delay, rand_min, rand_max, word_min, word_max,
                      typo_chance, typo_len_min, typo_len_max,
                      typo_delay_min_ms, typo_delay_max_ms),
                daemon=True
            ).start()

    countdown(startup_delay)

def type_text(text, delay, rand_min, rand_max, word_min, word_max,
              typo_chance, typo_len_min, typo_len_max,
              typo_delay_min_ms, typo_delay_max_ms):
    global stop_typing, is_typing

    def make_typo(length):
        chars = "abcdefghijklmnopqrstuvwxyz0123456789"
        return ''.join(random.choice(chars) for _ in range(length))

    words = text.split(" ")
    for i, word in enumerate(words):
        if stop_typing:
            break
        j = 0
        while j < len(word):
            if stop_typing:
                break
            actual_delay = delay + random.uniform(rand_min, rand_max)
            actual_delay = max(0, actual_delay)

            # Possibly insert a typo
            if random.random() < typo_chance:
                typo_length = random.randint(typo_len_min, typo_len_max)
                typo_text = make_typo(typo_length)
                for c in typo_text:
                    pyautogui.write(c, interval=actual_delay)
                typo_delay = random.uniform(typo_delay_min_ms, typo_delay_max_ms) / 1000.0
                time.sleep(typo_delay)
                for _ in typo_text:
                    pyautogui.press('backspace')

            pyautogui.write(word[j], interval=actual_delay)
            j += 1

        if i < len(words) - 1:
            pyautogui.write(" ")
            word_delay = random.uniform(word_min, word_max)
            time.sleep(word_delay)

    info_label.config(text="Typing finished" if not stop_typing else "Typing stopped")
    is_typing = False

def stop():
    global stop_typing
    stop_typing = True
    info_label.config(text="Stopped typing")

def remove_focus(event):
    widget = event.widget
    if widget not in (text_box, delay_entry, rand_min_entry, rand_max_entry,
                      word_min_entry, word_max_entry, startup_delay_entry,
                      typo_entry, typo_len_min_entry, typo_len_max_entry,
                      typo_delay_min_entry, typo_delay_max_entry):
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

# --- GUI ---
root = tk.Tk()
root.title("Auto Typer")

root.bind("<Button-1>", remove_focus)

text_box = tk.Text(root, height=10, width=50)
text_box.pack(pady=10)

# Keystroke delay
tk.Label(root, text="Base delay between keystrokes (ms):").pack()
delay_entry = tk.Entry(root); delay_entry.insert(0, "100"); delay_entry.pack(pady=5)

tk.Label(root, text="Random delay range per keystroke (ms, min-max):").pack()
rand_frame = tk.Frame(root); rand_frame.pack(pady=5)
rand_min_entry = tk.Entry(rand_frame, width=5); rand_min_entry.insert(0,"0"); rand_min_entry.pack(side=tk.LEFT, padx=(0,5))
rand_max_entry = tk.Entry(rand_frame, width=5); rand_max_entry.insert(0,"0"); rand_max_entry.pack(side=tk.LEFT)

tk.Label(root, text="Word delay range (ms, min-max):").pack()
word_frame = tk.Frame(root); word_frame.pack(pady=5)
word_min_entry = tk.Entry(word_frame, width=5); word_min_entry.insert(0,"0"); word_min_entry.pack(side=tk.LEFT, padx=(0,5))
word_max_entry = tk.Entry(word_frame, width=5); word_max_entry.insert(0,"0"); word_max_entry.pack(side=tk.LEFT)

tk.Label(root, text="Startup delay before typing (ms):").pack()
startup_delay_entry = tk.Entry(root); startup_delay_entry.insert(0,"3000"); startup_delay_entry.pack(pady=5)

tk.Label(root, text="Chance of making a typo (%):").pack()
typo_entry = tk.Entry(root); typo_entry.insert(0,"0"); typo_entry.pack(pady=5)

tk.Label(root, text="Typo length range (chars, min-max):").pack()
typo_len_frame = tk.Frame(root); typo_len_frame.pack(pady=5)
typo_len_min_entry = tk.Entry(typo_len_frame, width=5); typo_len_min_entry.insert(0,"1"); typo_len_min_entry.pack(side=tk.LEFT, padx=(0,5))
typo_len_max_entry = tk.Entry(typo_len_frame, width=5); typo_len_max_entry.insert(0,"1"); typo_len_max_entry.pack(side=tk.LEFT)

tk.Label(root, text="Typo correction delay range (ms, min-max):").pack()
typo_delay_frame = tk.Frame(root); typo_delay_frame.pack(pady=5)
typo_delay_min_entry = tk.Entry(typo_delay_frame, width=5); typo_delay_min_entry.insert(0,"50"); typo_delay_min_entry.pack(side=tk.LEFT, padx=(0,5))
typo_delay_max_entry = tk.Entry(typo_delay_frame, width=5); typo_delay_max_entry.insert(0,"50"); typo_delay_max_entry.pack(side=tk.LEFT)

start_button = tk.Button(root, text="Start Typing", command=start_typing); start_button.pack(pady=5)
stop_button = tk.Button(root, text="Stop", command=stop); stop_button.pack(pady=5)

start_key_label = tk.Label(root, text="Start Key: Not set"); start_key_label.pack()
set_start_button = tk.Button(root, text="Set Start Key", command=set_start_key); set_start_button.pack(pady=2)

stop_key_label = tk.Label(root, text="Stop Key: Not set"); stop_key_label.pack()
set_stop_button = tk.Button(root, text="Set Stop Key", command=set_stop_key); set_stop_button.pack(pady=2)

info_label = tk.Label(root, text=""); info_label.pack(pady=10)

pyautogui.FAILSAFE = True
root.mainloop()
