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
        
        # Variabel untuk bahasa
        self.language = tk.StringVar(value="indonesia")
        self.translations = {
            "indonesia": {
                "app_title": "Backup Guard",
                "source_path": "Path Sumber:",
                "output_path": "Path Output:",
                "interval": "Interval Backup:",
                "max_files": "Jumlah MAX File:",
                "auto_delete": "Aktifkan penghapusan otomatis",
                "mode": "Mode Backup:",
                "format_title": "Format Nama Backup",
                "time_format": "Format Waktu:",
                "use_original": "Gunakan nama asli file",
                "custom_name": "Nama Khusus:",
                "compression": "Tipe Backup:",
                "start": "Mulai Proses",
                "stop": "Hentikan Proses",
                "settings": "Pengaturan",
                "language": "Bahasa",
                "indonesia": "Indonesia",
                "english": "Inggris",
                "invalid_source": "Path sumber tidak valid.",
                "output_error": "Gagal membuat folder output:",
                "backup_failed": "Backup Gagal",
                "error": "Error",
                "seconds": "detik",
                "minutes": "menit",
                "hours": "jam",
                "device_minutes": "Menit Perangkat",
                "device_hours": "Jam Perangkat",
                "folder": "Folder",
                "file": "File",
                "zip": "ZIP",
                "none": "Tidak Ada",
                "cleanup_error": "Error saat membersihkan backup lama:"
            },
            "english": {
                "app_title": "Backup Guard",
                "source_path": "Source Path:",
                "output_path": "Output Path:",
                "interval": "Backup Interval:",
                "max_files": "Max Files:",
                "auto_delete": "Enable auto deletion",
                "mode": "Backup Mode:",
                "format_title": "Backup Name Format",
                "time_format": "Time Format:",
                "use_original": "Use original file name",
                "custom_name": "Custom Name:",
                "compression": "Backup Type:",
                "start": "Start Process",
                "stop": "Stop Process",
                "settings": "Settings",
                "language": "Language",
                "indonesia": "Indonesian",
                "english": "English",
                "invalid_source": "Invalid source path.",
                "output_error": "Failed to create output folder:",
                "backup_failed": "Backup Failed",
                "error": "Error",
                "seconds": "seconds",
                "minutes": "minutes",
                "hours": "hours",
                "device_minutes": "Device Minutes",
                "device_hours": "Device Hours",
                "folder": "Folder",
                "file": "File",
                "zip": "ZIP",
                "none": "None",
                "cleanup_error": "Error while cleaning old backups:"
            }
        }

        self.source_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.interval_value = tk.IntVar(value=30)
        self.interval_unit = tk.StringVar(value="minutes")
        self.max_files = tk.IntVar(value=5)
        self.limit_enabled = tk.BooleanVar(value=True)
        self.mode = tk.StringVar(value="Folder")
        
        # Variabel untuk fitur tambahan
        self.date_format = tk.StringVar(value="tanggal/bulan/tahun_jam")
        self.use_original_name = tk.BooleanVar(value=False)
        self.custom_name = tk.StringVar()
        self.compression_type = tk.StringVar(value="ZIP")

        self.load_config()
        self.build_ui()
        self.prepare_temp_folder()

    def translate(self, key):
        """Mengambil terjemahan berdasarkan kunci dan bahasa saat ini"""
        lang = self.language.get()
        return self.translations[lang].get(key, key)

    def update_ui_language(self):
        """Memperbarui semua teks UI sesuai bahasa yang dipilih"""
        self.root.title(self.translate("app_title"))
        
        # Update label dan tombol
        self.source_label.config(text=self.translate("source_path"))
        self.output_label.config(text=self.translate("output_path"))
        self.interval_label.config(text=self.translate("interval"))
        self.max_files_label.config(text=self.translate("max_files"))
        self.mode_label.config(text=self.translate("mode"))
        self.format_frame.config(text=self.translate("format_title"))
        self.time_format_label.config(text=self.translate("time_format"))
        self.use_original_check.config(text=self.translate("use_original"))
        self.custom_name_label.config(text=self.translate("custom_name"))
        self.compression_label.config(text=self.translate("compression"))
        
        # Update combobox values
        self.interval_unit_combobox['values'] = [
            self.translate("seconds"),
            self.translate("minutes"),
            self.translate("hours"),
            self.translate("device_minutes"),
            self.translate("device_hours")
        ]
        
        self.mode_combobox['values'] = [self.translate("folder"), self.translate("file")]
        self.compression_combobox['values'] = [self.translate("zip"), self.translate("none")]
        
        # Update tombol start/stop
        if self.running:
            self.start_button.config(text=self.translate("stop"))
        else:
            self.start_button.config(text=self.translate("start"))

    def build_ui(self):
        padding = {'padx': 10, 'pady': 5}
        row = 0

        # Frame untuk header (judul + tombol settings)
        header_frame = tk.Frame(self.root)
        header_frame.grid(row=row, column=0, columnspan=3, sticky="ew")
        
        # Judul aplikasi
        tk.Label(header_frame, text=self.translate("app_title"), font=('Helvetica', 14, 'bold')).pack(side="left")
        
        # Tombol settings di pojok kanan
        settings_icon = u"\u2699"  # Unicode gear icon
        self.settings_button = tk.Button(header_frame, text=settings_icon, command=self.show_settings_menu, 
                                       font=('Helvetica', 12), bd=0, relief=tk.FLAT)
        self.settings_button.pack(side="right")
        row += 1

        # Source path
        self.source_label = tk.Label(self.root, text=self.translate("source_path"))
        self.source_label.grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.source_path, width=50).grid(row=row, column=1, **padding)
        tk.Button(self.root, text="Browse", command=self.browse_source).grid(row=row, column=2, **padding)
        row += 1

        # Output path
        self.output_label = tk.Label(self.root, text=self.translate("output_path"))
        self.output_label.grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.output_path, width=50).grid(row=row, column=1, **padding)
        tk.Button(self.root, text="Browse", command=self.browse_output).grid(row=row, column=2, **padding)
        row += 1

        # Interval backup
        self.interval_label = tk.Label(self.root, text=self.translate("interval"))
        self.interval_label.grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.interval_value, width=10).grid(row=row, column=1, sticky="w", **padding)
        
        self.interval_unit_combobox = ttk.Combobox(self.root, textvariable=self.interval_unit, width=15)
        self.interval_unit_combobox.grid(row=row, column=1, sticky="e", **padding)
        row += 1

        # Max files
        self.max_files_label = tk.Label(self.root, text=self.translate("max_files"))
        self.max_files_label.grid(row=row, column=0, sticky="w", **padding)
        tk.Entry(self.root, textvariable=self.max_files, width=10).grid(row=row, column=1, sticky="w", **padding)
        
        self.limit_check = tk.Checkbutton(self.root, text=self.translate("auto_delete"), variable=self.limit_enabled)
        self.limit_check.grid(row=row, column=1, sticky="e", **padding)
        row += 1

        # Mode backup
        self.mode_label = tk.Label(self.root, text=self.translate("mode"))
        self.mode_label.grid(row=row, column=0, sticky="w", **padding)
        
        self.mode_combobox = ttk.Combobox(self.root, textvariable=self.mode, width=10)
        self.mode_combobox.grid(row=row, column=1, sticky="w", **padding)
        row += 1

        # Frame untuk format nama backup
        self.format_frame = tk.LabelFrame(self.root, text=self.translate("format_title"), padx=5, pady=5)
        self.format_frame.grid(row=row, column=0, columnspan=3, sticky="we", **padding)
        row += 1

        # Pilihan format tanggal
        self.time_format_label = tk.Label(self.format_frame, text=self.translate("time_format"))
        self.time_format_label.grid(row=0, column=0, sticky="w", **padding)
        
        ttk.Combobox(self.format_frame, textvariable=self.date_format, 
                    values=[
                        "tanggal/bulan/tahun_jam",
                        "jam_tanggal/bulan/tahun",
                        "bulan/tanggal/tahun_jam",
                        "tahun/bulan/tanggal_jam",
                        "tahun/tanggal/bulan_jam"
                    ], width=25).grid(row=0, column=1, sticky="w", **padding)

        # Checkbox untuk menggunakan nama asli file
        self.use_original_check = tk.Checkbutton(self.format_frame, text=self.translate("use_original"), 
                                              variable=self.use_original_name)
        self.use_original_check.grid(row=1, column=0, columnspan=2, sticky="w", **padding)

        # Input untuk nama khusus
        self.custom_name_label = tk.Label(self.format_frame, text=self.translate("custom_name"))
        self.custom_name_label.grid(row=2, column=0, sticky="w", **padding)
        tk.Entry(self.format_frame, textvariable=self.custom_name, width=30).grid(row=2, column=1, sticky="w", **padding)

        # Pilihan tipe kompresi
        self.compression_label = tk.Label(self.format_frame, text=self.translate("compression"))
        self.compression_label.grid(row=3, column=0, sticky="w", **padding)
        
        self.compression_combobox = ttk.Combobox(self.format_frame, textvariable=self.compression_type, width=10)
        self.compression_combobox.grid(row=3, column=1, sticky="w", **padding)

        # Tombol start/stop
        self.start_button = tk.Button(self.root, text=self.translate("start"), command=self.toggle_process, 
                                    bg="#4CAF50", fg="white")
        self.start_button.grid(row=row, column=0, columnspan=3, pady=20)
        row += 1

        # Update nilai combobox setelah dibuat
        self.update_ui_language()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_settings_menu(self):
        """Menampilkan menu settings"""
        menu = tk.Menu(self.root, tearoff=0)
        
        # Submenu bahasa
        lang_menu = tk.Menu(menu, tearoff=0)
        lang_menu.add_radiobutton(label=self.translate("indonesia"), variable=self.language, 
                                value="indonesia", command=self.change_language)
        lang_menu.add_radiobutton(label=self.translate("english"), variable=self.language, 
                                value="english", command=self.change_language)
        
        menu.add_cascade(label=self.translate("language"), menu=lang_menu)
        
        # Tampilkan menu di posisi mouse
        try:
            menu.tk_popup(self.settings_button.winfo_rootx(), 
                         self.settings_button.winfo_rooty() + self.settings_button.winfo_height())
        finally:
            menu.grab_release()

    def change_language(self):
        """Mengubah bahasa aplikasi"""
        # Simpan nilai combobox sebelum update
        old_interval_unit = self.interval_unit.get()
        old_mode = self.mode.get()
        old_compression = self.compression_type.get()
        
        # Update UI
        self.update_ui_language()
        
        # Kembalikan nilai yang dipilih setelah update
        self.interval_unit.set(old_interval_unit)
        self.mode.set(old_mode)
        self.compression_type.set(old_compression)
        
        # Simpan konfigurasi
        self.save_config()

    def browse_source(self):
        if self.mode.get() == self.translate("file").capitalize():
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
                messagebox.showerror(self.translate("error"), self.translate("invalid_source"))
                return
            
            if not os.path.exists(self.output_path.get()):
                try:
                    os.makedirs(self.output_path.get())
                except Exception as e:
                    messagebox.showerror(self.translate("error"), f"{self.translate('output_error')} {str(e)}")
                    return
            
            self.clear_temp_folder()
            self.running = True
            self.stop_requested = False
            self.last_backup_time = None
            self.start_button.configure(text=self.translate("stop"), bg="#f44336")
            threading.Thread(target=self.run_backup_loop, daemon=True).start()

    def stop_backup(self):
        self.running = False
        self.start_button.configure(text=self.translate("start"), bg="#4CAF50")
        self.start_button.config(state=tk.NORMAL)
        self.clear_temp_folder()

    def should_run_backup(self):
        now = datetime.now()
        unit = self.interval_unit.get()
        value = self.interval_value.get()
        
        if self.last_backup_time is None:
            return True
            
        if unit == self.translate("seconds"):
            return (now - self.last_backup_time).total_seconds() >= value
        elif unit == self.translate("minutes"):
            return (now - self.last_backup_time).total_seconds() >= value * 60
        elif unit == self.translate("hours"):
            return (now - self.last_backup_time).total_seconds() >= value * 3600
        elif unit == self.translate("device_minutes"):
            return now.minute != self.last_backup_time.minute
        elif unit == self.translate("device_hours"):
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
                
            time.sleep(1)

    def generate_backup_name(self):
        now = datetime.now()
        
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
        
        name_parts = []
        
        if self.use_original_name.get():
            original_name = os.path.basename(self.source_path.get())
            original_name = os.path.splitext(original_name)[0]
            name_parts.append(original_name.replace(' ', '_'))
        
        if self.custom_name.get():
            name_parts.append(self.custom_name.get().replace(' ', '_'))
        
        name_parts.append(timestamp)
        
        backup_name = "_".join(name_parts)
        
        if self.compression_type.get() == self.translate("zip").capitalize():
            backup_name += ".zip"
        elif self.mode.get() == self.translate("file").capitalize():
            original_ext = os.path.splitext(self.source_path.get())[1]
            backup_name += original_ext
        
        return backup_name

    def prepare_temp_folder(self):
        if not os.path.exists(TEMP_FOLDER):
            os.makedirs(TEMP_FOLDER)
        return TEMP_FOLDER

    def clear_temp_folder(self):
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
            self.clear_temp_folder()
            
            backup_name = self.generate_backup_name()
            final_backup_path = os.path.join(self.output_path.get(), backup_name)
            
            if self.mode.get() == self.translate("folder").capitalize():
                temp_source = os.path.join(TEMP_FOLDER, os.path.basename(self.source_path.get()))
                shutil.copytree(self.source_path.get(), temp_source)
                
                if self.compression_type.get() == self.translate("zip").capitalize():
                    shutil.make_archive(final_backup_path.replace(".zip", ""), 'zip', TEMP_FOLDER)
                else:
                    shutil.move(temp_source, final_backup_path)
            else:
                temp_source = os.path.join(TEMP_FOLDER, os.path.basename(self.source_path.get()))
                shutil.copy2(self.source_path.get(), temp_source)
                
                if self.compression_type.get() == self.translate("zip").capitalize():
                    shutil.make_archive(final_backup_path.replace(".zip", ""), 'zip', TEMP_FOLDER)
                else:
                    shutil.move(temp_source, final_backup_path)
            
            self.clear_temp_folder()
            
        except Exception as e:
            messagebox.showerror(self.translate("backup_failed"), f"Terjadi error: {str(e)}")
            return

        if self.limit_enabled.get():
            self.cleanup_old_backups()

    def cleanup_old_backups(self):
        try:
            if self.compression_type.get() == self.translate("zip").capitalize():
                files = [f for f in os.listdir(self.output_path.get()) if f.endswith(".zip")]
            else:
                if self.mode.get() == self.translate("folder").capitalize():
                    files = [f for f in os.listdir(self.output_path.get()) 
                            if os.path.isdir(os.path.join(self.output_path.get(), f))]
                else:
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
            print(f"{self.translate('cleanup_error')} {str(e)}")

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
            "compression_type": self.compression_type.get(),
            "language": self.language.get()
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
                self.interval_unit.set(config.get("unit", "minutes"))
                self.max_files.set(config.get("max_files", 5))
                self.limit_enabled.set(config.get("limit_enabled", True))
                self.mode.set(config.get("mode", "Folder"))
                self.date_format.set(config.get("date_format", "tanggal/bulan/tahun_jam"))
                self.use_original_name.set(config.get("use_original_name", False))
                self.custom_name.set(config.get("custom_name", ""))
                self.compression_type.set(config.get("compression_type", "ZIP"))
                self.language.set(config.get("language", "indonesia"))

if __name__ == "__main__":
    root = tk.Tk()
    app = BackupGuard(root)
    root.mainloop()