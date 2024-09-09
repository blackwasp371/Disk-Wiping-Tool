import os
import sys
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import psutil
from typing import Literal

# Constants for Windows System
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3

PatternType = Literal['zeros', 'ones', 'random']

def install_modules():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])

try:
    import psutil
except ModuleNotFoundError:
    install_modules()
    import psutil

def generate_pattern(size: int, pattern_type: PatternType = 'random') -> bytes:
    if pattern_type == 'zeros':
        return b'\x00' * size
    elif pattern_type == 'ones':
        return b'\xFF' * size
    else:
        return os.urandom(size)

def wipe_disk_linux(disk_name: str, pattern_type: PatternType = 'random', passes: int = 3) -> None:
    try:
        with open(disk_name, 'rb+') as disk:
            disk.seek(0, os.SEEK_END)
            disk_size: int = disk.tell()
            disk.seek(0)

            buffer_size: int = 512
            num_sectors: int = disk_size // buffer_size

            for times in range(passes):
                for sector in range(num_sectors):
                    buffer: bytes = generate_pattern(buffer_size, pattern_type)
                    disk.write(buffer)
                print(f"Pass {times + 1} complete.")
            disk.flush()
            os.fsync(disk.fileno())
        print("The Disk Wipe was Completed.")
    except OSError as e:
        print(f"Failed to open or write to the disk: {e}")
        sys.exit(503)

class DiskWiperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Wiper")
        self.root.geometry("500x400")

        self.partitions = psutil.disk_partitions()

        self.create_widgets()

    def create_widgets(self):
        self.partition_label = tk.Label(self.root, text="Select Partition:")
        self.partition_label.pack(pady=10)

        self.partition_combo = ttk.Combobox(self.root, values=[p.device for p in self.partitions])
        self.partition_combo.pack(pady=10)

        self.pattern_label = tk.Label(self.root, text="Choose Pattern:")
        self.pattern_label.pack(pady=10)

        self.pattern_combo = ttk.Combobox(self.root, values=['zeros', 'ones', 'random'], state='readonly')
        self.pattern_combo.current(2)  # Default to 'random'
        self.pattern_combo.pack(pady=10)

        self.passes_label = tk.Label(self.root, text="Number of Passes:")
        self.passes_label.pack(pady=10)

        self.passes_entry = tk.Entry(self.root)
        self.passes_entry.insert(0, '3')  # Default to 3 passes
        self.passes_entry.pack(pady=10)

        self.wipe_button = tk.Button(self.root, text="Wipe Disk", command=self.wipe_disk)
        self.wipe_button.pack(pady=20)

    def wipe_disk(self):
        selected_partition = self.partition_combo.get()
        pattern = self.pattern_combo.get()
        passes = self.passes_entry.get()

        if not selected_partition:
            messagebox.showerror("Error", "Please select a partition to wipe.")
            return

        if not passes.isdigit() or int(passes) < 1:
            messagebox.showerror("Error", "Passes should be a positive integer.")
            return

        passes = int(passes)

        if messagebox.askyesno("Confirmation", "Are you sure you want to wipe the disk? This action is irreversible!"):
            system_type = platform.system()

            if system_type == 'Linux':
                wipe_disk_linux(selected_partition, pattern, passes)
            else:
                messagebox.showerror("Error", f"Unsupported operating system: {system_type}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DiskWiperApp(root)
    root.mainloop()
