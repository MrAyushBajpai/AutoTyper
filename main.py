import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import threading
import keyboard
import random
import json
import os
from datetime import datetime

# --- Global Variables ---
stop_typing = False
is_typing = False
key_listeners = {}
profiles_dir = "typer_profiles"

# --- Profile Management ---
def ensure_profiles_dir():
    """Create profiles directory if it doesn't exist"""
    if not os.path.exists(profiles_dir):
        os.makedirs(profiles_dir)

def save_profile():
    """Save current settings to a profile"""
    ensure_profiles_dir()
    profile_name = profile_combo.get().strip()
    
    if not profile_name:
        messagebox.showwarning("Warning", "Please enter a profile name")
        return
    
    profile_data = {
        "base_delay": delay_entry.get(),
        "rand_min": rand_min_entry.get(),
        "rand_max": rand_max_entry.get(),
        "word_min": word_min_entry.get(),
        "word_max": word_max_entry.get(),
        "startup_delay": startup_delay_entry.get(),
        "typo_chance": typo_entry.get(),
        "typo_len_min": typo_len_min_entry.get(),
        "typo_len_max": typo_len_max_entry.get(),
        "typo_delay_min": typo_delay_min_entry.get(),
        "typo_delay_max": typo_delay_max_entry.get(),
        "letters": letters_var.get(),
        "numbers": numbers_var.get(),
        "special": special_var.get(),
        "text": text_box.get("1.0", tk.END).rstrip("\n")
    }
    
    filepath = os.path.join(profiles_dir, f"{profile_name}.json")
    with open(filepath, 'w') as f:
        json.dump(profile_data, f, indent=2)
    
    update_profile_list()
    update_status(f"Profile '{profile_name}' saved", "green")

def load_profile():
    """Load settings from a profile"""
    profile_name = profile_combo.get().strip()
    if not profile_name:
        return
    
    filepath = os.path.join(profiles_dir, f"{profile_name}.json")
    if not os.path.exists(filepath):
        messagebox.showerror("Error", f"Profile '{profile_name}' not found")
        return
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Load settings
        delay_entry.delete(0, tk.END)
        delay_entry.insert(0, data.get("base_delay", "100"))
        
        rand_min_entry.delete(0, tk.END)
        rand_min_entry.insert(0, data.get("rand_min", "0"))
        
        rand_max_entry.delete(0, tk.END)
        rand_max_entry.insert(0, data.get("rand_max", "0"))
        
        word_min_entry.delete(0, tk.END)
        word_min_entry.insert(0, data.get("word_min", "0"))
        
        word_max_entry.delete(0, tk.END)
        word_max_entry.insert(0, data.get("word_max", "0"))
        
        startup_delay_entry.delete(0, tk.END)
        startup_delay_entry.insert(0, data.get("startup_delay", "3000"))
        
        typo_entry.delete(0, tk.END)
        typo_entry.insert(0, data.get("typo_chance", "0"))
        
        typo_len_min_entry.delete(0, tk.END)
        typo_len_min_entry.insert(0, data.get("typo_len_min", "1"))
        
        typo_len_max_entry.delete(0, tk.END)
        typo_len_max_entry.insert(0, data.get("typo_len_max", "1"))
        
        typo_delay_min_entry.delete(0, tk.END)
        typo_delay_min_entry.insert(0, data.get("typo_delay_min", "50"))
        
        typo_delay_max_entry.delete(0, tk.END)
        typo_delay_max_entry.insert(0, data.get("typo_delay_max", "50"))
        
        letters_var.set(data.get("letters", True))
        numbers_var.set(data.get("numbers", False))
        special_var.set(data.get("special", False))
        
        text_box.delete("1.0", tk.END)
        text_box.insert("1.0", data.get("text", ""))
        
        update_status(f"Profile '{profile_name}' loaded", "green")
        
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load profile: {str(e)}")

def delete_profile():
    """Delete a saved profile"""
    profile_name = profile_combo.get().strip()
    if not profile_name:
        return
    
    if messagebox.askyesno("Confirm", f"Delete profile '{profile_name}'?"):
        filepath = os.path.join(profiles_dir, f"{profile_name}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            update_profile_list()
            profile_combo.set("")
            update_status(f"Profile '{profile_name}' deleted", "orange")

def update_profile_list():
    """Update the profile dropdown list"""
    ensure_profiles_dir()
    profiles = [f[:-5] for f in os.listdir(profiles_dir) if f.endswith('.json')]
    profile_combo['values'] = profiles

# --- Utility Functions ---
def validate_number(value, default, min_val=0, max_val=None):
    """Validate and return a number with bounds checking"""
    try:
        num = int(value)
        if num < min_val:
            return min_val
        if max_val is not None and num > max_val:
            return max_val
        return num
    except ValueError:
        return default

def update_status(message, color="black"):
    """Update status label with color"""
    info_label.config(text=message, foreground=color)
    # Auto-clear status after 5 seconds
    root.after(5000, lambda: info_label.config(text="", foreground="black"))

def update_progress(current, total):
    """Update progress bar"""
    if total > 0:
        progress = (current / total) * 100
        progress_bar['value'] = progress
        progress_label.config(text=f"{current}/{total} characters")
    else:
        progress_bar['value'] = 0
        progress_label.config(text="")

# --- Main Functions ---
def start_typing():
    global stop_typing, is_typing
    
    if is_typing:
        update_status("Already typing!", "red")
        return
    
    text = text_box.get("1.0", tk.END).rstrip("\n")
    if not text:
        update_status("Text box is empty!", "red")
        return
    
    # Validate all inputs
    delay_ms = validate_number(delay_entry.get(), 100, 0, 10000)
    rand_min_ms = validate_number(rand_min_entry.get(), 0, 0, 5000)
    rand_max_ms = validate_number(rand_max_entry.get(), 0, rand_min_ms, 5000)
    word_min_ms = validate_number(word_min_entry.get(), 0, 0, 10000)
    word_max_ms = validate_number(word_max_entry.get(), 0, word_min_ms, 10000)
    startup_delay_ms = validate_number(startup_delay_entry.get(), 3000, 0, 60000)
    
    try:
        typo_chance = float(typo_entry.get()) / 100.0
        typo_chance = max(0, min(1, typo_chance))
    except ValueError:
        typo_chance = 0.0
    
    typo_len_min = validate_number(typo_len_min_entry.get(), 1, 1, 10)
    typo_len_max = validate_number(typo_len_max_entry.get(), typo_len_min, typo_len_min, 10)
    typo_delay_min_ms = validate_number(typo_delay_min_entry.get(), 50, 0, 5000)
    typo_delay_max_ms = validate_number(typo_delay_max_entry.get(), typo_delay_min_ms, typo_delay_min_ms, 5000)
    
    stop_typing = False
    is_typing = True
    
    # Convert to seconds
    delay = delay_ms / 1000.0
    rand_min, rand_max = rand_min_ms / 1000.0, rand_max_ms / 1000.0
    word_min, word_max = word_min_ms / 1000.0, word_max_ms / 1000.0
    startup_delay = startup_delay_ms / 1000.0
    
    # Update character count
    char_count_label.config(text=f"Total characters: {len(text)}")
    
    # Start countdown
    def countdown(seconds_remaining):
        global is_typing
        if stop_typing:
            start_button.config(text="Start Typing", state=tk.NORMAL)
            stop_button.config(state=tk.DISABLED)
            is_typing = False
            update_status("Startup cancelled", "orange")
            return
        
        if seconds_remaining > 0:
            ms_remaining = int(seconds_remaining * 1000)
            start_button.config(text=f"Starting in {ms_remaining}ms...", state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
            root.after(100, countdown, seconds_remaining - 0.1)
        else:
            start_button.config(text="Typing...", state=tk.DISABLED)
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
        chars = ""
        if letters_var.get():
            chars += "abcdefghijklmnopqrstuvwxyz"
        if numbers_var.get():
            chars += "0123456789"
        if special_var.get():
            chars += "!@#$%^&*()_+-=[]{}|;:',.<>/?"
        if not chars:
            chars = "abcdefghijklmnopqrstuvwxyz"
        return ''.join(random.choice(chars) for _ in range(length))
    
    total_chars = len(text)
    chars_typed = 0
    
    words = text.split(" ")
    for i, word in enumerate(words):
        if stop_typing:
            break
        
        for j, char in enumerate(word):
            if stop_typing:
                break
            
            actual_delay = delay + random.uniform(rand_min, rand_max)
            actual_delay = max(0, actual_delay)
            
            # Possibly insert a typo BEFORE typing the correct character
            if random.random() < typo_chance:
                typo_length = random.randint(typo_len_min, typo_len_max)
                typo_text = make_typo(typo_length)
                
                # Type the typo characters
                for c in typo_text:
                    pyautogui.write(c, interval=actual_delay)
                
                # Wait before correcting
                typo_delay = random.uniform(typo_delay_min_ms, typo_delay_max_ms) / 1000.0
                time.sleep(typo_delay)
                
                # Backspace the typo characters
                for _ in typo_text:
                    pyautogui.press('backspace')
                    time.sleep(0.01)  # Small delay between backspaces for reliability
            
            # NOW type the correct character
            pyautogui.write(char, interval=actual_delay)
            chars_typed += 1
            
            # Update progress in GUI thread
            root.after(0, update_progress, chars_typed, total_chars)
        
        # Add space between words
        if i < len(words) - 1:
            pyautogui.write(" ")
            chars_typed += 1
            root.after(0, update_progress, chars_typed, total_chars)
            
            word_delay = random.uniform(word_min, word_max)
            time.sleep(word_delay)
    
    # Reset UI
    root.after(0, lambda: (
        start_button.config(text="Start Typing", state=tk.NORMAL),
        stop_button.config(state=tk.DISABLED),
        progress_bar.config(value=0),
        progress_label.config(text=""),
        update_status("Typing finished" if not stop_typing else "Typing stopped", "green")
    ))
    
    is_typing = False

def stop():
    global stop_typing, is_typing
    stop_typing = True
    is_typing = False
    update_status("Stopped typing", "orange")
    start_button.config(text="Start Typing", state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    progress_bar['value'] = 0
    progress_label.config(text="")

def load_text_file():
    """Load text from a file"""
    filepath = filedialog.askopenfilename(
        title="Select text file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if filepath:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            text_box.delete("1.0", tk.END)
            text_box.insert("1.0", content)
            update_status(f"Loaded {os.path.basename(filepath)}", "green")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load file: {str(e)}")

def clear_text():
    """Clear the text box"""
    if text_box.get("1.0", tk.END).strip():
        if messagebox.askyesno("Confirm", "Clear all text?"):
            text_box.delete("1.0", tk.END)
            char_count_label.config(text="Total characters: 0")
            update_status("Text cleared", "blue")

def update_char_count(event=None):
    """Update character count display"""
    text = text_box.get("1.0", tk.END).rstrip("\n")
    char_count_label.config(text=f"Total characters: {len(text)}")

# --- Hotkey Functions ---
def set_start_key():
    if "start" in key_listeners:
        keyboard.remove_hotkey(key_listeners["start"])
        key_listeners.pop("start")
        start_key_label.config(text="Not set")
    wait_for_key("start")

def set_stop_key():
    if "stop" in key_listeners:
        keyboard.remove_hotkey(key_listeners["stop"])
        key_listeners.pop("stop")
        stop_key_label.config(text="Not set")
    wait_for_key("stop")

def wait_for_key(action):
    """Wait for user to press a key to set as hotkey"""
    root.focus_set()
    update_status(f"Press a key to set as {action} hotkey...", "blue")
    
    # Store the hook so we can unhook it later
    hook_id = None
    
    def assign_key(event):
        nonlocal hook_id
        if event.event_type == keyboard.KEY_DOWN:
            key = event.name
            
            # Set the hotkey
            if action == "start":
                set_hotkey("start", key, lambda: root.after(0, start_typing))
                start_key_label.config(text=key.upper())
                update_status(f"Start key set to: {key.upper()}", "green")
            else:
                set_hotkey("stop", key, lambda: root.after(0, stop))
                stop_key_label.config(text=key.upper())
                update_status(f"Stop key set to: {key.upper()}", "green")
            
            # Remove the hook
            if hook_id:
                keyboard.unhook(hook_id)
            
            # Return False to stop processing
            return False
    
    # Hook keyboard events
    hook_id = keyboard.hook(assign_key, suppress=False)

def set_hotkey(name, key, func):
    """Set a hotkey for a specific action"""
    global key_listeners
    
    # Remove old hotkey if exists
    if name in key_listeners:
        try:
            keyboard.remove_hotkey(key_listeners[name])
        except:
            pass
    
    # Add new hotkey
    try:
        listener = keyboard.add_hotkey(key, func)
        key_listeners[name] = listener
    except Exception as e:
        update_status(f"Error setting hotkey: {str(e)}", "red")

# --- GUI Setup ---
root = tk.Tk()
root.title("Enhanced Auto Typer")
root.geometry("700x850")

# Create notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=5)

# Main tab
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text="Main")

# Text Frame
text_frame = ttk.LabelFrame(main_tab, text="Text to Type", padding=10)
text_frame.pack(fill="both", expand=True, padx=10, pady=5)

# Text controls
text_controls = ttk.Frame(text_frame)
text_controls.pack(fill="x", pady=(0, 5))

ttk.Button(text_controls, text="Load File", command=load_text_file).pack(side=tk.LEFT, padx=2)
ttk.Button(text_controls, text="Clear", command=clear_text).pack(side=tk.LEFT, padx=2)
char_count_label = ttk.Label(text_controls, text="Total characters: 0")
char_count_label.pack(side=tk.RIGHT, padx=5)

# Text box with scrollbar
text_scroll = ttk.Scrollbar(text_frame)
text_box = tk.Text(text_frame, height=10, width=60, yscrollcommand=text_scroll.set)
text_scroll.config(command=text_box.yview)
text_box.pack(side=tk.LEFT, fill="both", expand=True)
text_scroll.pack(side=tk.RIGHT, fill="y")
text_box.bind('<KeyRelease>', update_char_count)

# Settings tab
settings_tab = ttk.Frame(notebook)
notebook.add(settings_tab, text="Settings")

# Delay Settings
delay_frame = ttk.LabelFrame(settings_tab, text="Delay Settings", padding=10)
delay_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(delay_frame, text="Base delay (ms):").grid(row=0, column=0, sticky="w", pady=2)
delay_entry = ttk.Entry(delay_frame, width=10)
delay_entry.insert(0, "100")
delay_entry.grid(row=0, column=1, pady=2)

ttk.Label(delay_frame, text="Random delay range (ms):").grid(row=1, column=0, sticky="w", pady=2)
rand_frame = ttk.Frame(delay_frame)
rand_frame.grid(row=1, column=1, pady=2)
rand_min_entry = ttk.Entry(rand_frame, width=8)
rand_min_entry.insert(0, "0")
rand_min_entry.pack(side=tk.LEFT)
ttk.Label(rand_frame, text=" to ").pack(side=tk.LEFT)
rand_max_entry = ttk.Entry(rand_frame, width=8)
rand_max_entry.insert(0, "0")
rand_max_entry.pack(side=tk.LEFT)

ttk.Label(delay_frame, text="Word delay range (ms):").grid(row=2, column=0, sticky="w", pady=2)
word_frame = ttk.Frame(delay_frame)
word_frame.grid(row=2, column=1, pady=2)
word_min_entry = ttk.Entry(word_frame, width=8)
word_min_entry.insert(0, "0")
word_min_entry.pack(side=tk.LEFT)
ttk.Label(word_frame, text=" to ").pack(side=tk.LEFT)
word_max_entry = ttk.Entry(word_frame, width=8)
word_max_entry.insert(0, "0")
word_max_entry.pack(side=tk.LEFT)

ttk.Label(delay_frame, text="Startup delay (ms):").grid(row=3, column=0, sticky="w", pady=2)
startup_delay_entry = ttk.Entry(delay_frame, width=10)
startup_delay_entry.insert(0, "3000")
startup_delay_entry.grid(row=3, column=1, pady=2)

# Typo Settings
typo_frame = ttk.LabelFrame(settings_tab, text="Typo Settings", padding=10)
typo_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(typo_frame, text="Typo chance (%):").grid(row=0, column=0, sticky="w", pady=2)
typo_entry = ttk.Entry(typo_frame, width=10)
typo_entry.insert(0, "0")
typo_entry.grid(row=0, column=1, pady=2)

ttk.Label(typo_frame, text="Typo length range:").grid(row=1, column=0, sticky="w", pady=2)
typo_len_frame = ttk.Frame(typo_frame)
typo_len_frame.grid(row=1, column=1, pady=2)
typo_len_min_entry = ttk.Entry(typo_len_frame, width=8)
typo_len_min_entry.insert(0, "1")
typo_len_min_entry.pack(side=tk.LEFT)
ttk.Label(typo_len_frame, text=" to ").pack(side=tk.LEFT)
typo_len_max_entry = ttk.Entry(typo_len_frame, width=8)
typo_len_max_entry.insert(0, "1")
typo_len_max_entry.pack(side=tk.LEFT)

ttk.Label(typo_frame, text="Correction delay (ms):").grid(row=2, column=0, sticky="w", pady=2)
typo_delay_frame = ttk.Frame(typo_frame)
typo_delay_frame.grid(row=2, column=1, pady=2)
typo_delay_min_entry = ttk.Entry(typo_delay_frame, width=8)
typo_delay_min_entry.insert(0, "50")
typo_delay_min_entry.pack(side=tk.LEFT)
ttk.Label(typo_delay_frame, text=" to ").pack(side=tk.LEFT)
typo_delay_max_entry = ttk.Entry(typo_delay_frame, width=8)
typo_delay_max_entry.insert(0, "50")
typo_delay_max_entry.pack(side=tk.LEFT)

ttk.Label(typo_frame, text="Include in typos:").grid(row=3, column=0, sticky="w", pady=2)
typo_chars_frame = ttk.Frame(typo_frame)
typo_chars_frame.grid(row=3, column=1, pady=2)

letters_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=False)
special_var = tk.BooleanVar(value=False)

ttk.Checkbutton(typo_chars_frame, text="Letters", variable=letters_var).pack(side=tk.LEFT, padx=2)
ttk.Checkbutton(typo_chars_frame, text="Numbers", variable=numbers_var).pack(side=tk.LEFT, padx=2)
ttk.Checkbutton(typo_chars_frame, text="Special", variable=special_var).pack(side=tk.LEFT, padx=2)

# Profiles tab
profiles_tab = ttk.Frame(notebook)
notebook.add(profiles_tab, text="Profiles")

profile_frame = ttk.LabelFrame(profiles_tab, text="Profile Management", padding=10)
profile_frame.pack(fill="x", padx=10, pady=5)

ttk.Label(profile_frame, text="Profile:").grid(row=0, column=0, sticky="w", pady=5)
profile_combo = ttk.Combobox(profile_frame, width=25)
profile_combo.grid(row=0, column=1, pady=5, padx=5)

profile_buttons = ttk.Frame(profile_frame)
profile_buttons.grid(row=1, column=0, columnspan=2, pady=10)

ttk.Button(profile_buttons, text="Load", command=load_profile).pack(side=tk.LEFT, padx=2)
ttk.Button(profile_buttons, text="Save", command=save_profile).pack(side=tk.LEFT, padx=2)
ttk.Button(profile_buttons, text="Delete", command=delete_profile).pack(side=tk.LEFT, padx=2)

# Control Frame (outside notebook)
control_frame = ttk.Frame(root)
control_frame.pack(fill="x", padx=10, pady=5)

# Hotkeys
hotkey_frame = ttk.LabelFrame(control_frame, text="Hotkeys", padding=10)
hotkey_frame.pack(side=tk.LEFT, fill="x", expand=True, padx=5)

hotkey_grid = ttk.Frame(hotkey_frame)
hotkey_grid.pack()

ttk.Label(hotkey_grid, text="Start:").grid(row=0, column=0, sticky="w", padx=5)
start_key_label = ttk.Label(hotkey_grid, text="Not set", width=10)
start_key_label.grid(row=0, column=1, padx=5)
ttk.Button(hotkey_grid, text="Set", command=set_start_key, width=8).grid(row=0, column=2, padx=5)

ttk.Label(hotkey_grid, text="Stop:").grid(row=1, column=0, sticky="w", padx=5)
stop_key_label = ttk.Label(hotkey_grid, text="Not set", width=10)
stop_key_label.grid(row=1, column=1, padx=5)
ttk.Button(hotkey_grid, text="Set", command=set_stop_key, width=8).grid(row=1, column=2, padx=5)

# Action buttons
action_frame = ttk.Frame(control_frame)
action_frame.pack(side=tk.RIGHT, padx=5)

start_button = ttk.Button(action_frame, text="Start Typing", command=start_typing, width=15)
start_button.pack(pady=2)

stop_button = ttk.Button(action_frame, text="Stop", command=stop, width=15, state=tk.DISABLED)
stop_button.pack(pady=2)

# Progress Frame
progress_frame = ttk.Frame(root)
progress_frame.pack(fill="x", padx=10, pady=5)

progress_bar = ttk.Progressbar(progress_frame, mode='determinate', length=400)
progress_bar.pack(side=tk.LEFT, padx=5)

progress_label = ttk.Label(progress_frame, text="")
progress_label.pack(side=tk.LEFT, padx=5)

# Status bar
status_frame = ttk.Frame(root)
status_frame.pack(fill="x", side=tk.BOTTOM, padx=10, pady=5)

info_label = ttk.Label(status_frame, text="", foreground="black")
info_label.pack(side=tk.LEFT)

# Initialize
pyautogui.FAILSAFE = True
update_profile_list()
update_char_count()

# Run
root.mainloop()