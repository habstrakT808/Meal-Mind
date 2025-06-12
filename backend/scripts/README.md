# Scripts MealMind

Folder ini berisi tool dan script utility untuk aplikasi MealMind.

## SQLite Tools

File `sqlite_tools.py` menyediakan fungsi untuk:

1. Backup database SQLite:
   ```bash
   python scripts/sqlite_tools.py backup
   ```
2. Restore database SQLite dari backup:
   ```bash
   python scripts/sqlite_tools.py restore --backup-file backups/nama_file_backup.db
   ```

## Menambahkan Script Baru

Jika Anda ingin menambahkan script baru:

1. Simpan file dengan format `nama_script.py`
2. Tambahkan docstring yang menjelaskan fungsi script
3. Tambahkan argumen command-line yang diperlukan menggunakan `argparse`
4. Jelaskan penggunaan script di README ini
