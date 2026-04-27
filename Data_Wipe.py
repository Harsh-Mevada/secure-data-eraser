import os
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class DataWipeGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("DataWipe Secure Erasure Utility")
        self.geometry("570x480")
        self.configure(bg="#23272E")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#2E3440")
        style.configure("TLabel", background="#23272E", foreground="#E5E9F0", font=("Segoe UI", 11))
        style.configure("TLabelframe", background="#2E3440", foreground="#88C0D0")
        style.configure("TLabelframe.Label", background="#2E3440", foreground="#88C0D0", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", background="#5E81AC", foreground="#ECEFF4", font=("Segoe UI", 11, "bold"))
        style.configure("TProgressbar", troughcolor="#4C566A", background="#A3BE8C", thickness=20)

        file_frame = ttk.Labelframe(self, text="File Selection", padding=12)
        file_frame.pack(fill="x", padx=18, pady=(18, 6))
        self.file_listbox = tk.Listbox(file_frame, height=5, bg="#3B4252", fg="#D8DEE9", font=("Segoe UI", 10))
        self.file_listbox.pack(side="left", expand=True, fill="x", pady=6, padx=(0, 8))

        add_btn = ttk.Button(file_frame, text="Add", command=self.add_files)
        add_btn.pack(side="top", padx=4, pady=(0, 4))

        remove_btn = ttk.Button(file_frame, text="Remove", command=self.remove_selected)
        remove_btn.pack(side="top", padx=4, pady=(4, 0))

        method_frame = ttk.Labelframe(self, text="Erasure Method", padding=12)
        method_frame.pack(fill="x", padx=18, pady=6)

        ttk.Label(method_frame, text="Choose method:").pack(side="left")
        self.method_var = tk.StringVar(value="Quick Wipe")
        ttk.Combobox(method_frame, textvariable=self.method_var,
                     values=["Quick Wipe", "DOD 5220.22-M", "Gutmann (35 Passes)"],
                     state="readonly", width=24, font=("Segoe UI", 10)).pack(side="left", padx=12)

        action_frame = ttk.Frame(self, padding=10)
        action_frame.pack(fill="x", padx=18, pady=6)

        self.start_btn = ttk.Button(action_frame, text="Start Erasure", command=self.start_erasure)
        self.start_btn.pack(side="left", padx=8)

        self.cancel_btn = ttk.Button(action_frame, text="Cancel", command=self.cancel_erasure)
        self.cancel_btn.pack(side="left", padx=8)

        progress_frame = ttk.Labelframe(self, text="Progress", padding=12)
        progress_frame.pack(fill="x", padx=18, pady=6)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", padx=6, pady=6)

        self.status_var = tk.StringVar(value="Ready.")
        status_frame = ttk.Frame(self)
        status_frame.pack(fill="x", padx=18, pady=(6, 18))

        status_label = ttk.Label(status_frame, relief="sunken", textvariable=self.status_var, anchor="w")
        status_label.pack(fill="x")

    def add_files(self):
        files = filedialog.askopenfilenames(title="Select Files to Erase")
        protected_dirs = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Users\\Administrator"]
        protected_exts = [".exe", ".dll", ".sys"]

        for f in files:
            if any(f.startswith(dir_path) for dir_path in protected_dirs):
                messagebox.showerror("Protected File", f"Cannot select protected system file:\n{f}")
                continue
            if any(f.lower().endswith(ext) for ext in protected_exts):
                messagebox.showerror("Blocked File Type", f"Blocked file type: {f}")
                continue
            if f not in self.file_listbox.get(0, tk.END):
                self.file_listbox.insert(tk.END, f)

    def remove_selected(self):
        selected = self.file_listbox.curselection()
        for i in reversed(selected):
            self.file_listbox.delete(i)

    def start_erasure(self):
        count = self.file_listbox.size()
        if count == 0:
            messagebox.showwarning("No Files", "Please add files to erase.")
            return

        method = self.method_var.get()
        confirm = messagebox.askyesno("Confirm", f"Are you sure you want to securely erase {count} file(s) using '{method}'?")
        if not confirm:
            return

        self.status_var.set(f"Erasing {count} file(s) using '{method}'...")
        self.update_idletasks()

        for i in range(count):
            file_path = self.file_listbox.get(i)
            try:
                self.status_var.set(f"Erasing: {file_path}")
                self.update_idletasks()
                self.secure_erase(file_path, method)
            except Exception as e:
                self.status_var.set(f"Error on {file_path}: {e}")
                return
            self.progress_var.set((i + 1) / count * 100)
            self.update_idletasks()

        self.status_var.set("Erasure completed successfully.")
        self.file_listbox.delete(0, tk.END)

    def secure_erase(self, path, method):
        protected_dirs = ["C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)", "C:\\Users\\Administrator"]
        protected_exts = [".exe", ".dll", ".sys"]

        if any(path.startswith(p) for p in protected_dirs) or any(path.lower().endswith(ext) for ext in protected_exts):
            raise PermissionError("Attempt to erase protected or system-critical file!")

        if not os.path.isfile(path):
            raise FileNotFoundError("File not found")

        size = os.path.getsize(path)

        def write_pass(byte_value=None, random=False):
            with open(path, "r+b") as f:
                written = 0
                block_size = 4096
                while written < size:
                    to_write = min(size - written, block_size)
                    if random:
                        data = os.urandom(to_write)
                    else:
                        data = bytes([byte_value]) * to_write
                    f.write(data)
                    written += to_write
                f.flush()
                os.fsync(f.fileno())

        if method == "Quick Wipe":
            write_pass(0x00)
        elif method == "DOD 5220.22-M":
            write_pass(0x00)
            write_pass(0xFF)
            write_pass(random=True)
        elif method == "Gutmann (35 Passes)":
            for _ in range(35):
                write_pass(random=True)

        os.remove(path)

    def cancel_erasure(self):
        self.progress_var.set(0)
        self.status_var.set("Erasure cancelled.")

if __name__ == "__main__":
    app = DataWipeGUI()
    app.mainloop()
