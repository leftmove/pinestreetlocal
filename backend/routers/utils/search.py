import meilisearch
import motor.motor_asyncio

from dotenv import load_dotenv
from os import getenv
from tqdm import tqdm

from .mongo import *

load_dotenv()

# pyright: reportGeneralTypeIssues=false

MEILISEARCH_SERVER_URL = getenv("MEILISEARCH_SERVER_URL")
MEILISEARCH_MASTER_KEY = getenv("MEILISEARCH_MASTER_KEY")
MONGO_BACKUP_URL = getenv("MONGO_BACKUP_URL")
print("[ Search (Meilisearch) Initializing ] ...")

search = meilisearch.Client(MEILISEARCH_SERVER_URL, MEILISEARCH_MASTER_KEY)
companies_index = search.index("companies")


async def search_companies(query, options={}):
    result = companies_index.search(query, options)
    hits = result["hits"]

    return hits


print("[ Search (Meilisearch) Initialized ]")
