import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Konfigurasi dasar aplikasi"""
    SECRET_KEY = os.environ.get("SECRET_KEY", "ganti-secret-key-ini-di-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'expense_tracker.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    # Daftar kategori pengeluaran default
    CATEGORIES = [
        "Makanan & Minuman",
        "Transportasi",
        "Belanja",
        "Tagihan & Utilitas",
        "Hiburan",
        "Kesehatan",
        "Pendidikan",
        "Lainnya",
    ]
