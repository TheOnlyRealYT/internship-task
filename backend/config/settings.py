from dotenv import load_dotenv, find_dotenv
from os import getenv

load_dotenv(find_dotenv(".env"))
DATABASE_URL = getenv("DATABASE_URL", "")
if DATABASE_URL is None:
    raise Exception("No Database URL Found")

STALE_CUTOFF = getenv("STALE_CUTOFF", 7)
ARCHIVE_CUTOFF = getenv("ARCHIVE_CUTOFF", 30)