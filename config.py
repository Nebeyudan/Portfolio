import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-key")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin")
    DB_PATH = os.path.join(os.path.dirname(__file__), "portfolio.db")
    # You can extend these later (e.g., MAIL settings if you add SMTP)