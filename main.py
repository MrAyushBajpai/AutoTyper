import tkinter as tk
import pyautogui
import time
import threading
import keyboard

stop_typing = False
start_key = None
stop_key = None
key_listeners = {}

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
    print("Stopped typing")

def remove_focus(event):
    widget = event.widget
    if widget != text_box:
        root.focus()

def set_start_key():
    wait_for_key("start")

def set_stop_key():
    wait_for_key("stop")

def wait_for_key(action):
    # Remove focus from text box so single-character keys don't appear
    root.focus_set()

    info_label.config(text=f"Press a key to set as {action} hotkey...")

    def on_key_press(event):
        global start_key, stop_key

        key = event.name
        if action == "start":
            set_hotkey("start", key, start_typing)
            start_key_label.config(text=f"Start Key: {key.upper()}")
        else:
            set_hotkey("stop", key, stop)
            stop_key_label.config(text=f"Stop Key: {key.upper()}")

        info_label.config(text=f"{action.capitalize()} key set to: {key.upper()}")
        keyboard.unhook(on_key_press)  # stop listening for assignment

    keyboard.hook(on_key_press)

def set_hotkey(name, key, func):
    """Safely update a global hotkey listener."""
    global key_listeners

    # Remove previous hotkey if it exists
    if name in key_listeners:
        keyboard.remove_hotkey(key_listeners[name])

    # Add new global hotkey
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
info_label.pack(pady=5)



root.mainloop()
