import os
import threading
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox

class M3UCrafterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SteamOS_Emu_M3U_Crafter")
        self.root.geometry("600x400")

        # Selected folder path
        self.folder_path = tk.StringVar()

        # Folder selection
        tk.Label(root, text="Target Folder:").pack(pady=5)
        folder_frame = tk.Frame(root)
        folder_frame.pack(pady=5, fill="x", padx=10)
        tk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side="left", expand=True, fill="x")
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side="left", padx=5)

        # Craft button
        self.craft_button = tk.Button(root, text="Craft", command=self.start_crafting, state="disabled")
        self.craft_button.pack(pady=10)

        # Status text area
        tk.Label(root, text="Status:").pack(pady=5)
        self.status_box = scrolledtext.ScrolledText(root, height=10, width=70, state="disabled")
        self.status_box.pack(padx=10, pady=5, fill="both", expand=True)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.craft_button.config(state="normal")

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
