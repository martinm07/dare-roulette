import os

from dotenv import load_dotenv

from flaskapp import create_app

load_dotenv()

print("DATABASE_URI:", os.environ.get("SQLALCHEMY_DATABASE_URI"))
app = create_app()
