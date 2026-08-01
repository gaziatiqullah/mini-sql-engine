import tkinter as tk
from tkinter import scrolledtext, messagebox
import subprocess
import os
import sys

# Define the path to the compiled C executable
# Adjusts automatically depending on Windows (.exe) or Mac/Linux
EXE_NAME = "sql_engine.exe" if os.name == 'nt' else "sql_engine"
ENGINE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), EXE_NAME)

def execute_query():
    # 1. Get query from text box
    query = query_input.get("1.0", tk.END).strip()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a SQL query.")
        return

    # 2. Append 'exit;' so the C program terminates automatically
    full_input = query + "\nexit;\n"

    try:
        # 3. Run the compiled C engine via subprocess
        process = subprocess.run(
            [ENGINE_PATH],
            input=full_input,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(ENGINE_PATH) # Run in root to access data/ folder
        )

        # 4. Clean up the output (remove the command-line prompts)
        raw_output = process.stdout + process.stderr
        clean_lines = []
        for line in raw_output.split('\n'):
            # Strip out the interactive CLI elements from main.c
            if "Mini SQL Engine" in line or "sql> " in line or "Goodbye!" in line:
                continue
            clean_lines.append(line)

        final_output = "\n".join(clean_lines).strip()

        # 5. Display the result
        result_display.config(state=tk.NORMAL)
        result_display.delete("1.0", tk.END)
        result_display.insert(tk.END, final_output if final_output else "Query executed successfully.")
        result_display.config(state=tk.DISABLED)

    except FileNotFoundError:
        messagebox.showerror("Execution Error", f"Could not find {EXE_NAME}. Did you run 'mingw32-make' first?")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_input():
    query_input.delete("1.0", tk.END)
    result_display.config(state=tk.NORMAL)
    result_display.delete("1.0", tk.END)
    result_display.config(state=tk.DISABLED)

# --- GUI Layout Setup ---
root = tk.Tk()
root.title("Mini SQL Engine - GUI")
root.geometry("800x600")
root.configure(bg="#2d2d2d")

# Styling variables
bg_color = "#2d2d2d"
fg_color = "#ffffff"
text_bg = "#1e1e1e"
font_tuple = ("Consolas", 12)

# Input Frame
input_frame = tk.Frame(root, bg=bg_color)
input_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(input_frame, text="Enter SQL Query:", bg=bg_color, fg=fg_color, font=("Consolas", 12, "bold")).pack(anchor=tk.W)

query_input = scrolledtext.ScrolledText(input_frame, height=5, bg=text_bg, fg=fg_color, font=font_tuple, insertbackground="white")
query_input.pack(fill=tk.X, pady=5)

# Buttons Frame
btn_frame = tk.Frame(root, bg=bg_color)
btn_frame.pack(fill=tk.X, padx=10)

run_btn = tk.Button(btn_frame, text="Execute Query", bg="#4CAF50", fg="white", font=("Consolas", 11, "bold"), command=execute_query)
run_btn.pack(side=tk.LEFT, padx=5)

clear_btn = tk.Button(btn_frame, text="Clear", bg="#f44336", fg="white", font=("Consolas", 11, "bold"), command=clear_input)
clear_btn.pack(side=tk.LEFT, padx=5)

# Output Frame
output_frame = tk.Frame(root, bg=bg_color)
output_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

tk.Label(output_frame, text="Query Results:", bg=bg_color, fg=fg_color, font=("Consolas", 12, "bold")).pack(anchor=tk.W)

result_display = scrolledtext.ScrolledText(output_frame, bg=text_bg, fg="#4CAF50", font=font_tuple, state=tk.DISABLED)
result_display.pack(fill=tk.BOTH, expand=True, pady=5)

# Start Application
root.mainloop()