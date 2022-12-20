import os
from dotenv import load_dotenv

load_dotenv()

class Settings(object):
	port = int(os.environ.get("MY_APP_PORT"))
	cookie_secret= os.environ.get("MY_COOKIE_SECRET")
