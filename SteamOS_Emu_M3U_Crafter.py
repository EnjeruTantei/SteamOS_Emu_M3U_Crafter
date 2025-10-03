#!/usr/bin/env python3
import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import subprocess
import sys
import pathlib

CONFIG_FILE = os.path.expanduser("~/.m3u_crafter_lastdir")

class M3UCrafterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SteamOS_Emu_M3U_Crafter")
        self.root.geometry("600x400")

        # Load last folder if exists
        self.last_dir = self.load_last_dir()
        self.folder_path = tk.StringVar(value=self.last_dir)

        # Folder selection
        tk.Label(root, text="Target Folder:").pack(pady=5)
        folder_frame = tk.Frame(root)
        folder_frame.pack(pady=5, fill="x", padx=10)
        tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side="left", expand=True, fill="x")
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side="left", padx=5)

        # Craft button
        self.craft_button = tk.Button(root, text="Craft", command=self.start_crafting, state="normal" if self.last_dir else "disabled")
        self.craft_button.pack(pady=10)

        # Status text area
        tk.Label(root, text="Status:").pack(pady=5)
        self.status_box = scrolledtext.ScrolledText(root, height=10, width=70, state="disabled")
        self.status_box.pack(padx=10, pady=5, fill="both", expand=True)

    def load_last_dir(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return f.read().strip()
            except:
                return ""
        return ""

    def save_last_dir(self, folder):
        try:
            with open(CONFIG_FILE, "w") as f:
                f.write(folder)
        except:
            pass

    def browse_folder(self):
        folder = None
        # Try KDE Dolphin chooser if available
        if sys.platform.startswith("linux") and shutil.which("dolphin"):
            try:
                # Dolphin with --chooseDir prints the chosen directory to stdout
                proc = subprocess.run(
                    ["dolphin", "--chooseDir", self.last_dir or str(pathlib.Path.home())],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                if proc.returncode == 0:
                    folder = proc.stdout.strip()
            except Exception as e:
                self.update_status(f"Falling back to Tk dialog: {e}")

        # Fallback to Tk dialog
        if not folder:
            dir_ = self.last_dir if self.last_dir and os.path.isdir(self.last_dir) else os.path.expanduser("~")
    
            # Normalize path for Windows quirks
            dir_ = os.path.normpath(dir_)
            
            # If still rejected, fallback to parent directory
            if not os.path.exists(dir_):
                dir_ = os.path.dirname(dir_)
            if not os.path.isdir(dir_):
                dir_ = os.path.expanduser("~")
            
            print("self.last_dir", self.last_dir, "| using:", dir_)
            
            folder = filedialog.askdirectory(
                parent=self.root,
                initialdir=dir_,
                mustexist=True
            )

        if folder:
            self.folder_path.set(folder)
            self.craft_button.config(state="normal")
            self.save_last_dir(folder)
            self.last_dir = folder

    def start_crafting(self):
        folder = self.folder_path.get()
        if not folder:
            messagebox.showerror("Error", "Please select a folder first.")
            return

        self.craft_button.config(state="disabled")
        self.update_status("Starting crafting process...")

        thread = threading.Thread(target=self.craft_m3u, args=(folder,))
        thread.start()

    def craft_m3u(self, folder):
        try:
            root_name = os.path.basename(folder)
            parent_dir = os.path.dirname(folder)
            m3u_filename = f"{root_name}.m3u"
            m3u_path = os.path.join(folder, m3u_filename)

            # Step 1: Note folder name
            self.update_status(f"Step 1: Root folder name is '{root_name}'.")

            # Step 2: Create M3U file
            self.update_status(f"Step 2: Creating M3U file '{m3u_filename}'.")
            with open(m3u_path, "w", encoding="utf-8") as m3u_file:
                # Step 3: Index files
                self.update_status("Step 3: Indexing .cue and .bin files...")
                cue_files = []
                bin_files = []
                for root, _, files in os.walk(folder):
                    for file in sorted(files):
                        if file.lower().endswith(".cue"):
                            cue_files.append(os.path.join(root, file))
                        elif file.lower().endswith(".bin"):
                            bin_files.append(os.path.join(root, file))

                for f in cue_files + bin_files:
                    rel_path = os.path.relpath(f, folder)
                    m3u_file.write(rel_path + "\n")

            # Step 4: Rename root folder
            new_folder = os.path.join(parent_dir, f"{root_name}.m3u")
            self.update_status(f"Step 4: Renaming folder to '{new_folder}'.")
            os.rename(folder, new_folder)

            # Step 5: Success
            self.update_status("Step 5: Crafting successful!")
            messagebox.showinfo("Success", f"Crafting completed!\n\nCreated: {m3u_filename}")
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            messagebox.showerror("Error", f"Crafting failed:\n{e}")
        finally:
            self.craft_button.config(state="normal")

    def update_status(self, message):
        def append():
            self.status_box.config(state="normal")
            self.status_box.insert(tk.END, message + "\n")
            self.status_box.see(tk.END)
            self.status_box.config(state="disabled")
        self.root.after(0, append)


if __name__ == "__main__":
    root = tk.Tk()
    app = M3UCrafterApp(root)
    root.mainloop()
