import os
import time
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import json
from datetime import datetime

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_guard_config.json")
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backup_guard_temp")

class BackupGuard:
    def __init__(self, root):
        self.root = root
        self.root.title("Backup Guard")
        self.running = False
        self.currently_backing_up = False
        self.stop_requested = False
        self.last_backup_time = None

        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.interval_value = tk.IntVar(value=30)
        self.interval_unit = tk.StringVar(value="menit")
        self.max_files = tk.IntVar(value=5)
        self.limit_enabled = tk.BooleanVar(value=True)
        self.mode = tk.StringVar(value="Folder")
        
        # Variabel baru untuk fitur tambahan
        self.date_format = tk.StringVar(value="tanggal/bulan/tahun_jam")
        self.use_original_name = tk.BooleanVar(value=False)
        self.custom_name = tk.StringVar()
        self.compression_type = tk.StringVar(value="ZIP")

        self.load_config()
        self.build_ui()
        self.prepare_temp_folder()

    def build_ui(self):
        padding = {'padx': 10, 'pady': 5}
        row = 0

        tk.Label(self.root, text="Path Sumber:").grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.source_path, width=50).grid(row=row, column=1, **padding)
        tk.Button(self.root, text="Browse", command=self.browse_source).grid(row=row, column=2, **padding)
        row += 1

        tk.Label(self.root, text="Path Output:").grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.output_path, width=50).grid(row=row, column=1, **padding)
        tk.Button(self.root, text="Browse", command=self.browse_output).grid(row=row, column=2, **padding)
        row += 1

        tk.Label(self.root, text="Interval Backup:").grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.interval_value, width=10).grid(row=row, column=1, sticky="w", **padding)
        ttk.Combobox(self.root, textvariable=self.interval_unit, 
                    values=["detik", "menit", "jam", "Menit Perangkat", "Jam Perangkat"], 
                    width=15).grid(row=row, column=1, sticky="e", **padding)
        row += 1

        tk.Label(self.root, text="Jumlah MAX File:").grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.max_files, width=10).grid(row=row, column=1, sticky="w", **padding)
        tk.Checkbutton(self.root, text="Aktifkan penghapusan otomatis", variable=self.limit_enabled).grid(row=row, column=1, sticky="e", **padding)
        row += 1

        tk.Label(self.root, text="Mode Backup:").grid(row=row, column=0, sticky="w", **padding)
        ttk.Combobox(self.root, textvariable=self.mode, values=["Folder", "File"], width=10).grid(row=row, column=1, sticky="w", **padding)
        row += 1

        # Frame untuk format nama backup
        format_frame = tk.LabelFrame(self.root, text="Format Nama Backup", padx=5, pady=5)
        format_frame.grid(row=row, column=0, columnspan=3, sticky="we", **padding)
        row += 1

        # Pilihan format tanggal
        tk.Label(format_frame, text="Format Waktu:").grid(row=0, column=0, sticky="w", **padding)
        ttk.Combobox(format_frame, textvariable=self.date_format, 
                    values=[
                        "tanggal/bulan/tahun_jam",
                        "jam_tanggal/bulan/tahun",
                        "bulan/tanggal/tahun_jam",
                        "tahun/bulan/tanggal_jam",
                        "tahun/tanggal/bulan_jam"
                    ], width=25).grid(row=0, column=1, sticky="w", **padding)

        # Checkbox untuk menggunakan nama asli file
        tk.Checkbutton(format_frame, text="Gunakan nama asli file", variable=self.use_original_name).grid(row=1, column=0, columnspan=2, sticky="w", **padding)

        # Input untuk nama khusus
        tk.Label(format_frame, text="Nama Khusus:").grid(row=2, column=0, sticky="w", **padding)
        tk.Entry(format_frame, textvariable=self.custom_name, width=30).grid(row=2, column=1, sticky="w", **padding)

        # Pilihan tipe kompresi
        tk.Label(format_frame, text="Tipe Backup:").grid(row=3, column=0, sticky="w", **padding)
        ttk.Combobox(format_frame, textvariable=self.compression_type, values=["ZIP", "Tidak Ada"], width=10).grid(row=3, column=1, sticky="w", **padding)

        self.start_button = tk.Button(self.root, text="Mulai Proses", command=self.toggle_process, bg="#4CAF50", fg="white")
        self.start_button.grid(row=row, column=0, columnspan=3, pady=20)
        row += 1

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def browse_source(self):
        if self.mode.get() == "File":
            path = filedialog.askopenfilename()
        else:
            path = filedialog.askdirectory()
        if path:
            self.source_path.set(path)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_path.set(path)

    def toggle_process(self):
        if self.running:
            self.stop_requested = True
            self.start_button.config(state=tk.DISABLED)
            if not self.currently_backing_up:
                self.stop_backup()
        else:
            if not os.path.exists(self.source_path.get()):
                messagebox.showerror("Error", "Path sumber tidak valid.")
                return
            
            if not os.path.exists(self.output_path.get()):
                try:
                    os.makedirs(self.output_path.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal membuat folder output: {str(e)}")
                    return
            
            self.clear_temp_folder()
            self.running = True
            self.stop_requested = False
            self.last_backup_time = None
            self.start_button.configure(text="Hentikan Proses", bg="#f44336")
            threading.Thread(target=self.run_backup_loop, daemon=True).start()

    def stop_backup(self):
        self.running = False
        self.start_button.configure(text="Mulai Proses", bg="#4CAF50")
        self.start_button.config(state=tk.NORMAL)
        self.clear_temp_folder()

    def should_run_backup(self):
        now = datetime.now()
        unit = self.interval_unit.get()
        value = self.interval_value.get()
        
        if self.last_backup_time is None:
            return True
            
        if unit == "detik":
            return (now - self.last_backup_time).total_seconds() >= value
        elif unit == "menit":
            return (now - self.last_backup_time).total_seconds() >= value * 60
        elif unit == "jam":
            return (now - self.last_backup_time).total_seconds() >= value * 3600
        elif unit == "Menit Perangkat":
            return now.minute != self.last_backup_time.minute
        elif unit == "Jam Perangkat":
            return now.hour != self.last_backup_time.hour
            
        return False

    def run_backup_loop(self):
        while self.running and not self.stop_requested:
            if self.should_run_backup():
                self.currently_backing_up = True
                self.perform_backup()
                self.last_backup_time = datetime.now()
                self.currently_backing_up = False
            
            if self.stop_requested:
                self.stop_backup()
                break
                
            # Cek setiap 1 detik untuk responsif terhadap stop request
            time.sleep(1)

    def generate_backup_name(self):
        now = datetime.now()
        
        # Format tanggal sesuai pilihan
        date_format = self.date_format.get()
        if date_format == "tanggal/bulan/tahun_jam":
            timestamp = now.strftime("%d-%m-%Y_%H-%M")
        elif date_format == "jam_tanggal/bulan/tahun":
            timestamp = now.strftime("%H-%M_%d-%m-%Y")
        elif date_format == "bulan/tanggal/tahun_jam":
            timestamp = now.strftime("%m-%d-%Y_%H-%M")
        elif date_format == "tahun/bulan/tanggal_jam":
            timestamp = now.strftime("%Y-%m-%d_%H-%M")
        elif date_format == "tahun/tanggal/bulan_jam":
            timestamp = now.strftime("%Y-%d-%m_%H-%M")
        
        # Nama file backup
        name_parts = []
        
        # Tambahkan nama asli file jika diaktifkan
        if self.use_original_name.get():
            original_name = os.path.basename(self.source_path.get())
            original_name = os.path.splitext(original_name)[0]  # Hilangkan ekstensi
            name_parts.append(original_name.replace(' ', '_'))
        
        # Tambahkan nama khusus jika diisi
        if self.custom_name.get():
            name_parts.append(self.custom_name.get().replace(' ', '_'))
        
        # Tambahkan timestamp
        name_parts.append(timestamp)
        
        # Gabungkan semua bagian
        backup_name = "_".join(name_parts)
        
        # Tambahkan ekstensi
        if self.compression_type.get() == "ZIP":
            backup_name += ".zip"
        elif self.mode.get() == "File":
            # Pertahankan ekstensi asli jika mode file dan tidak dikompres
            original_ext = os.path.splitext(self.source_path.get())[1]
            backup_name += original_ext
        
        return backup_name

    def prepare_temp_folder(self):
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)
        return TEMP_FOLDER

    def clear_temp_folder(self):
        # Hapus semua isi folder temporary
        if os.path.exists(TEMP_FOLDER):
            for filename in os.listdir(TEMP_FOLDER):
                file_path = os.path.join(TEMP_FOLDER, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f"Gagal menghapus {file_path}. Reason: {e}")

    def perform_backup(self):
        try:
            # Bersihkan temporary folder sebelum memulai
            self.clear_temp_folder()
            
            backup_name = self.generate_backup_name()
            final_backup_path = os.path.join(self.output_path.get(), backup_name)
            
            if self.mode.get() == "Folder":
                # Backup folder
                temp_source = os.path.join(TEMP_FOLDER, os.path.basename(self.source_path.get()))
                shutil.copytree(self.source_path.get(), temp_source)
                
                if self.compression_type.get() == "ZIP":
                    # Kompres folder dari temporary
                    shutil.make_archive(final_backup_path.replace(".zip", ""), 'zip', TEMP_FOLDER)
                else:
                    # Pindahkan langsung dari temporary ke tujuan
                    shutil.move(temp_source, final_backup_path)
            else:
                # Backup file
                temp_source = os.path.join(TEMP_FOLDER, os.path.basename(self.source_path.get()))
                shutil.copy2(self.source_path.get(), temp_source)
                
                if self.compression_type.get() == "ZIP":
                    # Kompres file dari temporary
                    shutil.make_archive(final_backup_path.replace(".zip", ""), 'zip', TEMP_FOLDER)
                else:
                    # Pindahkan langsung dari temporary ke tujuan
                    shutil.move(temp_source, final_backup_path)
            
            # Bersihkan temporary setelah selesai
            self.clear_temp_folder()
            
        except Exception as e:
            messagebox.showerror("Backup Gagal", f"Terjadi error: {str(e)}")
            return

        if self.limit_enabled.get():
            self.cleanup_old_backups()

    def cleanup_old_backups(self):
        try:
            if self.compression_type.get() == "ZIP":
                files = [f for f in os.listdir(self.output_path.get()) if f.endswith(".zip")]
            else:
                if self.mode.get() == "Folder":
                    files = [f for f in os.listdir(self.output_path.get()) 
                            if os.path.isdir(os.path.join(self.output_path.get(), f))]
                else:
                    # Untuk file tanpa ekstensi khusus
                    source_ext = os.path.splitext(self.source_path.get())[1]
                    files = [f for f in os.listdir(self.output_path.get()) 
                            if f.endswith(source_ext)]
                    
            files = sorted(files, key=lambda x: os.path.getmtime(os.path.join(self.output_path.get(), x)))
            while len(files) > self.max_files.get():
                file_to_remove = os.path.join(self.output_path.get(), files.pop(0))
                if os.path.isdir(file_to_remove):
                    shutil.rmtree(file_to_remove)
                else:
                    os.remove(file_to_remove)
        except Exception as e:
            print(f"Error saat membersihkan backup lama: {str(e)}")

    def on_close(self):
        if self.running:
            self.stop_requested = True
            if not self.currently_backing_up:
                self.stop_backup()
                self.save_config()
                self.root.destroy()
        else:
            self.save_config()
            self.root.destroy()

    def save_config(self):
        config = {
            "source": self.source_path.get(),
            "output": self.output_path.get(),
            "interval": self.interval_value.get(),
            "unit": self.interval_unit.get(),
            "max_files": self.max_files.get(),
            "limit_enabled": self.limit_enabled.get(),
            "mode": self.mode.get(),
            "date_format": self.date_format.get(),
            "use_original_name": self.use_original_name.get(),
            "custom_name": self.custom_name.get(),
            "compression_type": self.compression_type.get()
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                self.source_path.set(config.get("source", ""))
                self.output_path.set(config.get("output", ""))
                self.interval_value.set(config.get("interval", 30))
                self.interval_unit.set(config.get("unit", "menit"))
                self.max_files.set(config.get("max_files", 5))
                self.limit_enabled.set(config.get("limit_enabled", True))
                self.mode.set(config.get("mode", "Folder"))
                self.date_format.set(config.get("date_format", "tanggal/bulan/tahun_jam"))
                self.use_original_name.set(config.get("use_original_name", False))
                self.custom_name.set(config.get("custom_name", ""))
                self.compression_type.set(config.get("compression_type", "ZIP"))

if __name__ == "__main__":
    root = tk.Tk()
    app = BackupGuard(root)
    root.mainloop()