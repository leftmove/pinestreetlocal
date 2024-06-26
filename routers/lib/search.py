import meilisearch

import os
import time

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
production_environment = True if ENVIRONMENT == "production" else False
if not production_environment:
    from dotenv import load_dotenv

    load_dotenv(".env")

MEILI_SERVER_URL = os.environ["MEILI_SERVER_URL"]
MEILI_MASTER_KEY = os.environ["MEILI_MASTER_KEY"]

search = meilisearch.Client(MEILI_SERVER_URL, MEILI_MASTER_KEY)
if "companies" not in [index.uid for index in search.get_indexes()["results"]]:
    search.create_index("companies", {"primaryKey": "cik"})
    time.sleep(3)
    search = meilisearch.Client(MEILI_SERVER_URL, MEILI_MASTER_KEY)
companies_index = search.index("companies")
companies_index.update_displayed_attributes(
    [
        "name",
        "cik",
        "tickers",
    ]
)
companies_index.update_searchable_attributes(["name", "tickers", "cik"])
companies_index.update_filterable_attributes(["thirteen_f"])


def search_companies(query, options={}):
    result = companies_index.search(query, options)
    hits = result["hits"]

    return hits
