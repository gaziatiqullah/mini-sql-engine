import customtkinter as ctk
from tkinter import messagebox
import subprocess
import os
from datetime import datetime

# --- Modern Theme Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENGINE = os.path.join(BASE_DIR, "sql_engine.exe" if os.name == 'nt' else "sql_engine")
DATA_DIR = os.path.join(BASE_DIR, "data")

class MiniSQLEngineApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Mini SQL Engine - University Project")
        self.geometry("1200x760")
        self.minsize(1000, 650)
        
        # Color Palette
        self.bg_color = "#0f172a"
        self.panel_color = "#1e293b"
        self.editor_bg = "#020617"
        self.accent_color = "#38bdf8"
        self.success_color = "#22c55e"
        self.error_color = "#ef4444"

        self.configure(fg_color=self.bg_color)
        
        self.build_header()
        self.build_body()
        self.load_example()
        self.refresh_tables()

    def build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))

        title = ctk.CTkLabel(header, text="Mini SQL Engine", font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"))
        title.pack(side="left")

        subtitle = ctk.CTkLabel(header, text="Flex + Bison + C + Python", font=ctk.CTkFont(family="Segoe UI", size=12), text_color="#94a3b8")
        subtitle.pack(side="left", padx=18, pady=(8, 0))

        self.status = ctk.CTkLabel(header, text="● Engine Ready", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.success_color)
        self.status.pack(side="right", pady=10)

    def build_body(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=24, pady=8)

        # Sidebar
        sidebar = ctk.CTkFrame(main, fg_color=self.panel_color, width=240, corner_radius=10)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)

        # Main Content Area
        center = ctk.CTkFrame(main, fg_color=self.panel_color, corner_radius=10)
        center.pack(side="left", fill="both", expand=True)

        self.build_sidebar(sidebar)
        self.build_editor(center)

    def build_sidebar(self, parent):
        # Database Section
        ctk.CTkLabel(parent, text="DATABASE", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=16, pady=(18, 8))

        self.tables_box = ctk.CTkTextbox(parent, height=120, fg_color=self.editor_bg, font=ctk.CTkFont(family="Consolas", size=12))
        self.tables_box.pack(fill="x", padx=14, pady=(0, 10))
        self.tables_box.configure(state="disabled")

        ctk.CTkButton(parent, text="↻ Refresh Tables", command=self.refresh_tables, fg_color="#334155", hover_color="#475569").pack(fill="x", padx=14)

        # Commands Section
        ctk.CTkLabel(parent, text="QUICK COMMANDS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8").pack(anchor="w", padx=16, pady=(24, 8))

        commands = [
            ("CREATE TABLE", "CREATE TABLE students (id INT, name VARCHAR, cgpa FLOAT);"),
            ("INSERT", "INSERT INTO students VALUES (1, 'Taiful', 3.50);"),
            ("SELECT ALL", "SELECT * FROM students;"),
            ("SELECT WHERE", "SELECT name FROM students WHERE cgpa > 3.0;"),
            ("AGGREGATE", "SELECT AVG(cgpa) FROM students;"),
            ("SUBQUERY", "SELECT * FROM students WHERE cgpa > (SELECT AVG(cgpa) FROM students);"),
            ("UPDATE", "UPDATE students SET cgpa = 4.0 WHERE id = 1;"),
            ("DELETE", "DELETE FROM students WHERE cgpa < 2.0;")
        ]

        # Use a scrollable frame for commands if they exceed sidebar height
        cmd_frame = ctk.CTkScrollableFrame(parent, fg_color="transparent")
        cmd_frame.pack(fill="both", expand=True, padx=5, pady=5)

        for name, sql in commands:
            ctk.CTkButton(
                cmd_frame, text=name, command=lambda value=sql: self.set_sql(value),
                fg_color="#334155", hover_color="#475569", anchor="w"
            ).pack(fill="x", padx=5, pady=3)

    def build_editor(self, parent):
        # Top Bar
        top = ctk.CTkFrame(parent, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(18, 8))

        ctk.CTkLabel(top, text="SQL QUERY EDITOR", font=ctk.CTkFont(size=14, weight="bold")).pack(side="left")

        ctk.CTkButton(top, text="Run SQL", command=self.run_sql, fg_color=self.accent_color, text_color="#082f49", hover_color="#0ea5e9", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=(10, 0))
        ctk.CTkButton(top, text="Clear", command=self.clear_all, fg_color="#334155", hover_color="#475569").pack(side="right")

        # Editor
        self.editor = ctk.CTkTextbox(parent, height=180, fg_color=self.editor_bg, font=ctk.CTkFont(family="Consolas", size=14))
        self.editor.pack(fill="x", padx=18)

        # Output Section
        ctk.CTkLabel(parent, text="RESULT / CONSOLE", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=18, pady=(14, 7))

        # Output Container (Holds either Text or Table)
        self.output_container = ctk.CTkFrame(parent, fg_color="transparent")
        self.output_container.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.console = ctk.CTkTextbox(self.output_container, fg_color=self.editor_bg, text_color="#cbd5e1", font=ctk.CTkFont(family="Consolas", size=13))
        self.console.pack(fill="both", expand=True)
        self.console.configure(state="disabled")
        
        self.table_frame = ctk.CTkScrollableFrame(self.output_container, fg_color=self.editor_bg)

    def set_sql(self, sql):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", sql)

    def clear_all(self):
        self.editor.delete("1.0", "end")
        self.show_console("Cleared.")

    def load_example(self):
        self.set_sql("SELECT * FROM students;")

    def refresh_tables(self):
        self.tables_box.configure(state="normal")
        self.tables_box.delete("1.0", "end")

        if os.path.exists(DATA_DIR):
            tables_found = False
            for filename in sorted(os.listdir(DATA_DIR)):
                if filename.lower().endswith(".csv"):
                    self.tables_box.insert("end", f"📄 {filename[:-4]}\n")
                    tables_found = True
            if not tables_found:
                self.tables_box.insert("end", "No tables found.")
        else:
            self.tables_box.insert("end", "Data directory missing.")
            
        self.tables_box.configure(state="disabled")

    def show_console(self, text, is_error=False):
        self.table_frame.pack_forget()
        self.console.pack(fill="both", expand=True)
        
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.insert("1.0", text)
        self.console.configure(text_color=self.error_color if is_error else "#cbd5e1", state="disabled")

    def show_table(self, headers, rows, messages):
        self.console.pack_forget()
        self.table_frame.pack(fill="both", expand=True)
        
        # Clear old table
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Render Headers
        for j, header in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold"), fg_color="#334155", corner_radius=6, padx=10, pady=5)
            lbl.grid(row=0, column=j, padx=2, pady=2, sticky="ew")

        # Render Data
        for i, row in enumerate(rows):
            for j, val in enumerate(row):
                lbl = ctk.CTkLabel(self.table_frame, text=val, fg_color="#1e293b", corner_radius=6, padx=10, pady=5)
                lbl.grid(row=i+1, column=j, padx=2, pady=2, sticky="ew")
                
        # Render Extra Messages (e.g. "x row(s) returned")
        if messages:
            msg = "\n".join(messages)
            msg_lbl = ctk.CTkLabel(self.table_frame, text=msg, text_color=self.success_color, font=ctk.CTkFont(weight="bold"))
            msg_lbl.grid(row=len(rows)+1, column=0, columnspan=len(headers), pady=(10, 0))

    def run_sql(self):
        if not os.path.exists(ENGINE):
            messagebox.showerror("Engine not built", "Please run 'mingw32-make' first.")
            return

        sql = self.editor.get("1.0", "end").strip()
        if not sql:
            messagebox.showwarning("Empty query", "Please enter an SQL query.")
            return

        started = datetime.now()
        full_input = sql + "\nexit;\n"

        try:
            result = subprocess.run([ENGINE], input=full_input, text=True, capture_output=True, cwd=BASE_DIR, timeout=15)
            elapsed = (datetime.now() - started).total_seconds()
            
            raw_output = result.stdout + result.stderr
            clean_lines = [line.strip() for line in raw_output.split('\n') if not any(ignore in line for ignore in ["Mini SQL Engine", "sql> ", "Goodbye!"]) and line.strip()]
            
            # Append execution time so it renders smoothly at the bottom of tables or messages
            clean_lines.append(f"[Execution time: {elapsed:.4f} seconds]")
            final_output = "\n".join(clean_lines).strip()

            # Check if execution failed at C level
            if result.returncode != 0 or "Error:" in final_output or "Syntax error:" in final_output:
                self.status.configure(text="● Query Error", text_color=self.error_color)
                self.show_console(final_output, is_error=True)
                return

            self.status.configure(text="● Engine Ready", text_color=self.success_color)

            # --- UPGRADED ASCII Table Parser ---
            # Now detects both standard (+---+) and aggregate (|---|) table borders
            if "|" in final_output and ("+---" in final_output or "|---" in final_output):
                data_lines = []
                message_lines = []
                
                for line in clean_lines:
                    if line.startswith("|"):
                        # Filter out inner horizontal dividers (e.g., |-------|)
                        if not line.replace("|", "").replace("-", "").replace("+", "").strip():
                            continue
                        data_lines.append(line)
                    elif line.startswith("+"):
                        # Filter out outer border lines (e.g., +-------+)
                        continue
                    else:
                        message_lines.append(line)

                if data_lines:
                    # Using [1:-1] safely drops the empty strings generated by splitting the outer left/right '|' borders
                    headers = [col.strip() for col in data_lines[0].split("|")][1:-1]
                    rows = [[col.strip() for col in line.split("|")][1:-1] for line in data_lines[1:]]
                    self.show_table(headers, rows, message_lines)
                    self.refresh_tables()
                    return

            # Standard Console Output (Fallback for INSERT, CREATE, etc.)
            self.show_console(final_output)
            self.refresh_tables()

        except Exception as error:
            self.show_console(f"SYSTEM ERROR: {str(error)}", is_error=True)
            self.status.configure(text="● Error", text_color=self.error_color)

if __name__ == "__main__":
    app = MiniSQLEngineApp()
    app.mainloop()