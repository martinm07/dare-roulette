from dotenv import load_dotenv

from flaskapp import create_app

load_dotenv()

app = create_app()
