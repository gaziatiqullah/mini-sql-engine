import os
import re
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog

# --- Modern Theme Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BASE = os.path.dirname(os.path.dirname(__file__))
EXE_NAME = "sql_engine.exe" if os.name == 'nt' else "sql_engine"
ENGINE_PATH = os.path.join(BASE, EXE_NAME)
DATA_DIR = os.path.join(BASE, "data")

class MiniSQLEngineApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Mini SQL Engine PRO")
        self.geometry("1280x820")
        self.minsize(1000, 680)

        os.makedirs(DATA_DIR, exist_ok=True)

        self.create_layout()
        self.create_sidebar()
        self.create_editor()
        self.create_console()
        
        self.refresh_objects()
        self.apply_syntax_tags()

    def create_layout(self):
        # Two main columns: Sidebar (Left) and Content (Right)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(2, weight=1)

        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_frame.grid_rowconfigure(1, weight=1) # Editor expands
        self.content_frame.grid_rowconfigure(3, weight=1) # Console expands

    def create_sidebar(self):
        # Title
        ctk.CTkLabel(self.sidebar_frame, text="Mini SQL Engine", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # Database Objects Explorer
        ctk.CTkLabel(self.sidebar_frame, text="DATABASE OBJECTS", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").grid(row=1, column=0, padx=20, sticky="w")
        
        self.objects_frame = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.objects_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        
        ctk.CTkButton(self.sidebar_frame, text="↻ Refresh Objects", fg_color="#333333", hover_color="#444444", command=self.refresh_objects).grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        # Quick SQL Snippets
        ctk.CTkLabel(self.sidebar_frame, text="QUICK SQL", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray").grid(row=4, column=0, padx=20, pady=(10, 5), sticky="w")
        
        snippets = [
            ("SELECT *", "SELECT * FROM students;"),
            ("WHERE Clause", "SELECT * FROM students WHERE gpa > 3.0;"),
            ("AGGREGATE", "SELECT AVG(gpa) FROM students;"),
            ("SUBQUERY", "SELECT name FROM students WHERE gpa > (SELECT AVG(gpa) FROM students);"),
            ("UPDATE", "UPDATE students SET gpa = 4.0 WHERE name = 'Alice';"),
            ("DELETE", "DELETE FROM students WHERE gpa < 2.0;")
        ]

        self.snippet_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.snippet_frame.grid(row=5, column=0, sticky="ew", padx=10, pady=(0, 20))

        for idx, (label, query) in enumerate(snippets):
            btn = ctk.CTkButton(self.snippet_frame, text=label, anchor="w", fg_color="transparent", text_color="#22b5e8", hover_color="#263449", command=lambda q=query: self.set_query(q))
            btn.grid(row=idx, column=0, sticky="ew", pady=2)

    def create_editor(self):
        # Header / Tool bar
        toolbar = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        ctk.CTkLabel(toolbar, text="SQL EDITOR", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
        
        ctk.CTkButton(toolbar, text="▶ Run SQL", fg_color="#28a745", hover_color="#218838", font=ctk.CTkFont(weight="bold"), command=self.run_sql).pack(side="right", padx=(10, 0))
        ctk.CTkButton(toolbar, text="Clear", fg_color="#dc3545", hover_color="#c82333", command=self.clear_editor).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Save", fg_color="#333333", hover_color="#444444", command=self.save_sql).pack(side="right", padx=5)
        ctk.CTkButton(toolbar, text="Open", fg_color="#333333", hover_color="#444444", command=self.open_sql).pack(side="right", padx=5)

        # Main Editor
        self.editor = ctk.CTkTextbox(self.content_frame, font=ctk.CTkFont(family="Consolas", size=14), corner_radius=10)
        self.editor.grid(row=1, column=0, sticky="nsew")
        self.editor.bind("<KeyRelease>", self.highlight_sql)

        # Default Text
        self.editor.insert("1.0", "CREATE TABLE students (id INT, name VARCHAR, gpa FLOAT);\nINSERT INTO students VALUES (1, 'Alice', 3.8);\nSELECT * FROM students;")
        self.highlight_sql()

    def create_console(self):
        ctk.CTkLabel(self.content_frame, text="RESULTS", font=ctk.CTkFont(size=14, weight="bold")).grid(row=2, column=0, sticky="w", pady=(15, 5))
        
        # Container 1: Text Results
        self.console = ctk.CTkTextbox(self.content_frame, font=ctk.CTkFont(family="Consolas", size=14), text_color="#28a745", corner_radius=10, state="disabled")
        self.console.grid(row=3, column=0, sticky="nsew")

        # Container 2: Dynamic Table Grid (Hidden by default)
        self.table_frame = ctk.CTkScrollableFrame(self.content_frame, fg_color="#1e1e1e", corner_radius=10)

    def apply_syntax_tags(self):
        # Configure tags on the underlying tkinter Text widget
        text_widget = self.editor._textbox
        text_widget.tag_configure("keyword", foreground="#569CD6")
        text_widget.tag_configure("string", foreground="#CE9178")
        text_widget.tag_configure("number", foreground="#B5CEA8")
        text_widget.tag_configure("type", foreground="#4EC9B0")

    def highlight_sql(self, event=None):
        text_widget = self.editor._textbox
        text = self.editor.get("1.0", "end")
        
        for tag in ("keyword", "string", "number", "type"):
            text_widget.tag_remove(tag, "1.0", "end")

        keywords = r"\b(CREATE|TABLE|INSERT|INTO|VALUES|SELECT|FROM|WHERE|UPDATE|SET|DELETE|COUNT|SUM|AVG|MIN|MAX)\b"
        types = r"\b(INT|VARCHAR|FLOAT)\b"

        for m in re.finditer(keywords, text, re.I):
            text_widget.tag_add("keyword", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(types, text, re.I):
            text_widget.tag_add("type", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r"'([^']|'')*'", text):
            text_widget.tag_add("string", f"1.0+{m.start()}c", f"1.0+{m.end()}c")
        for m in re.finditer(r"\b\d+(\.\d+)?\b", text):
            text_widget.tag_add("number", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    def refresh_objects(self):
        for widget in self.objects_frame.winfo_children():
            widget.destroy()

        if os.path.isdir(DATA_DIR):
            files = [f for f in sorted(os.listdir(DATA_DIR)) if f.endswith(".schema")]
            if not files:
                ctk.CTkLabel(self.objects_frame, text="No tables found.", text_color="gray").pack(anchor="w")
            
            for file in files:
                table_name = file.replace(".schema", "")
                ctk.CTkLabel(self.objects_frame, text=f"🗄️ {table_name}", font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=2)

    def set_query(self, query):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", query)
        self.highlight_sql()

    def clear_editor(self):
        self.set_query("")
        self.console.grid(row=3, column=0, sticky="nsew")
        self.table_frame.grid_forget()
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def open_sql(self):
        path = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql"), ("All files", "*.*")])
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.set_query(f.read())

    def save_sql(self):
        path = filedialog.asksaveasfilename(defaultextension=".sql", filetypes=[("SQL files", "*.sql")])
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", "end-1c"))

    def run_sql(self):
        query = self.editor.get("1.0", "end").strip()
        if not query:
            messagebox.showwarning("Input Error", "Please enter a SQL query.")
            return

        if not os.path.exists(ENGINE_PATH):
            messagebox.showerror("Execution Error", f"Could not find {EXE_NAME}. Run 'mingw32-make' first.")
            return

        full_input = query + "\nexit;\n"

        try:
            process = subprocess.run([ENGINE_PATH], input=full_input, capture_output=True, text=True, cwd=BASE)
            raw_output = process.stdout + process.stderr
            
            clean_lines = [line.strip() for line in raw_output.split('\n') if "Mini SQL Engine" not in line and "sql>" not in line and "Goodbye!" not in line and line.strip()]
            final_output = "\n".join(clean_lines).strip()

            # Dynamic Table Parsing
            if "+" in final_output and "|" in final_output:
                data_lines = [line for line in clean_lines if line.startswith("|")]
                message_lines = [line for line in clean_lines if not line.startswith("|") and not line.startswith("+")]

                if data_lines:
                    headers = [col.strip() for col in data_lines[0].split("|") if col.strip()]
                    rows = [[col.strip() for col in line.split("|") if col.strip()] for line in data_lines[1:]]

                    self.console.grid_forget()
                    self.table_frame.grid(row=3, column=0, sticky="nsew")
                    
                    for widget in self.table_frame.winfo_children():
                        widget.destroy()

                    for j, header in enumerate(headers):
                        ctk.CTkLabel(self.table_frame, text=header, font=ctk.CTkFont(weight="bold"), fg_color="#333333", corner_radius=6, padx=10, pady=8).grid(row=0, column=j, padx=2, pady=2, sticky="ew")

                    for i, row in enumerate(rows):
                        for j, val in enumerate(row):
                            ctk.CTkLabel(self.table_frame, text=val, fg_color="#2a2d2e", corner_radius=6, padx=10, pady=6).grid(row=i+1, column=j, padx=2, pady=2, sticky="ew")

                    if message_lines:
                        ctk.CTkLabel(self.table_frame, text="\n".join(message_lines), text_color="#28a745", font=ctk.CTkFont(weight="bold")).grid(row=len(rows)+1, column=0, columnspan=len(headers), pady=(10, 0))
                    
                    self.refresh_objects()
                    return

            # Standard Text Output
            self.table_frame.grid_forget()
            self.console.grid(row=3, column=0, sticky="nsew")
            self.console.configure(state="normal")
            self.console.delete("1.0", "end")
            self.console.insert("end", final_output if final_output else "Query executed successfully.")
            self.console.configure(state="disabled")
            self.refresh_objects()

        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = MiniSQLEngineApp()
    app.mainloop()