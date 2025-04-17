import os

import pymysql
from dotenv import load_dotenv

from flaskapp import create_app

load_dotenv()

pymysql.install_as_MySQLdb()

print("DATABASE_URI:", os.environ.get("SQLALCHEMY_DATABASE_URI"))
app = create_app()
