import customtkinter as ctk
from tkinter import messagebox
import subprocess
import os

# --- Modern Theme Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

EXE_NAME = "sql_engine.exe" if os.name == 'nt' else "sql_engine"
ENGINE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), EXE_NAME)

def execute_query():
    query = query_input.get("1.0", ctk.END).strip()
    if not query:
        messagebox.showwarning("Input Error", "Please enter a SQL query.")
        return

    full_input = query + "\nexit;\n"

    try:
        process = subprocess.run(
            [ENGINE_PATH],
            input=full_input,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(ENGINE_PATH)
        )

        raw_output = process.stdout + process.stderr
        clean_lines = []
        for line in raw_output.split('\n'):
            if "Mini SQL Engine" in line or "sql> " in line or "Goodbye!" in line:
                continue
            clean_lines.append(line.strip())

        final_output = "\n".join(clean_lines).strip()

        # --- ASCII Table Parser ---
        # If the output contains a table border (+---+) and columns (|), render a visual table
        if "+" in final_output and "|" in final_output:
            data_lines = [line for line in clean_lines if line.startswith("|")]
            message_lines = [line for line in clean_lines if not line.startswith("|") and not line.startswith("+") and line != ""]

            if data_lines:
                # Extract headers from the first line
                headers = [col.strip() for col in data_lines[0].split("|") if col.strip()]
                
                # Extract rows from the remaining lines
                rows = []
                for line in data_lines[1:]:
                    row_data = [col.strip() for col in line.split("|") if col.strip()]
                    if row_data:
                        rows.append(row_data)

                # Swap UI: Hide Textbox, Show Table Frame
                result_display.pack_forget()
                table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
                
                # Clear previous table data
                for widget in table_frame.winfo_children():
                    widget.destroy()

                # Render Headers
                for j, header in enumerate(headers):
                    lbl = ctk.CTkLabel(table_frame, text=header, font=ctk.CTkFont(weight="bold"), 
                                       fg_color="#333333", corner_radius=6, padx=10, pady=8)
                    lbl.grid(row=0, column=j, padx=2, pady=2, sticky="ew")

                # Render Data Rows
                for i, row in enumerate(rows):
                    for j, val in enumerate(row):
                        lbl = ctk.CTkLabel(table_frame, text=val, fg_color="#2a2d2e", 
                                           corner_radius=6, padx=10, pady=6)
                        lbl.grid(row=i+1, column=j, padx=2, pady=2, sticky="ew")

                # Render extra messages (like "1 row(s) returned.")
                if message_lines:
                    msg = "\n".join(message_lines)
                    msg_lbl = ctk.CTkLabel(table_frame, text=msg, text_color="#28a745", font=ctk.CTkFont(weight="bold"))
                    msg_lbl.grid(row=len(rows)+1, column=0, columnspan=len(headers), pady=(10, 0))
                
                return # Exit early so we don't hit the standard text display

        # --- Standard Text Display ---
        # If it's NOT a table (e.g., "1 row inserted."), hide the table frame and show text
        table_frame.pack_forget()
        result_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        result_display.configure(state="normal")
        result_display.delete("1.0", ctk.END)
        result_display.insert(ctk.END, final_output if final_output else "Query executed successfully.")
        result_display.configure(state="disabled")

    except FileNotFoundError:
        messagebox.showerror("Execution Error", f"Could not find {EXE_NAME}. Did you run 'mingw32-make' first?")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def clear_input():
    query_input.delete("1.0", ctk.END)
    # Hide table, show empty text box
    table_frame.pack_forget()
    result_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    result_display.configure(state="normal")
    result_display.delete("1.0", ctk.END)
    result_display.configure(state="disabled")

# --- GUI Layout Setup ---
root = ctk.CTk()
root.title("Mini SQL Engine")
root.geometry("850x650")

main_frame = ctk.CTkFrame(root, corner_radius=15)
main_frame.pack(pady=20, padx=20, fill="both", expand=True)

title_label = ctk.CTkLabel(main_frame, text="Mini SQL Engine", font=ctk.CTkFont(size=24, weight="bold"))
title_label.pack(pady=(15, 10))

input_label = ctk.CTkLabel(main_frame, text="Enter SQL Query:", font=ctk.CTkFont(size=14))
input_label.pack(anchor="w", padx=20)

query_input = ctk.CTkTextbox(main_frame, height=100, corner_radius=10, font=ctk.CTkFont(family="Consolas", size=14))
query_input.pack(fill="x", padx=20, pady=(5, 15))

btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
btn_frame.pack(fill="x", padx=20, pady=5)

run_btn = ctk.CTkButton(btn_frame, text="Execute Query", fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(weight="bold"), command=execute_query)
run_btn.pack(side="left", padx=(0, 10))

clear_btn = ctk.CTkButton(btn_frame, text="Clear", fg_color="#dc3545", hover_color="#c82333", font=ctk.CTkFont(weight="bold"), command=clear_input)
clear_btn.pack(side="left")

output_label = ctk.CTkLabel(main_frame, text="Query Results:", font=ctk.CTkFont(size=14))
output_label.pack(anchor="w", padx=20, pady=(15, 5))

# Container 1: The standard text box (for status messages)
result_display = ctk.CTkTextbox(main_frame, corner_radius=10, font=ctk.CTkFont(family="Consolas", size=14), text_color="#28a745", state="disabled")
result_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))

# Container 2: The Data Grid (Hidden by default, shown when a table is detected)
table_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")

root.mainloop()