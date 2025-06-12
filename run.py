import os
import sys

# Tambahkan direktori backend ke path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend')))

# Import dan jalankan aplikasi dari backend
from backend.run import app

if __name__ == '__main__':
    # Dapatkan port dari variabel lingkungan atau gunakan default 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 