from pymongo import MongoClient

import os
import logging

from datetime import datetime

ENVIRONMENT = os.environ.get("ENVIRONMENT", "development")
production_environment = True if ENVIRONMENT == "production" else False
if not production_environment:
    from dotenv import load_dotenv

    load_dotenv(".env.development")

MONGO_SERVER_URL = os.environ["MONGO_SERVER_URL"]
logging.info("[ Database (MongoDB) Initializing ] ...")

client = MongoClient(MONGO_SERVER_URL)
db = client["wallstreetlocal"]
main = db["filers"]
stocks = db["stocks"]
companies = db["companies"]
logs = db["logs"]
statistics = db["statistics"]


def check_stock(ticker):
    stock = stocks.find_one({"ticker": ticker})
    if stock == None:
        return False
    else:
        return True


def search_stocks(pipeline):
    cursor = stocks.aggregate(pipeline)
    return cursor


def find_stock(field, value):
    result = stocks.find_one({field: value})
    return result


def find_stocks(field, value):
    results = stocks.find({field: value}, {"_id": 0})
    return results


def edit_stock(query, value):
    stocks.update_one(query, value)


def add_stock(stock):
    stocks.insert_one(stock)


def find_filer(cik, project={"_id": 0}):
    result = main.find_one({"cik": cik}, project)
    return result


def find_filers(query, project={"_id": 0}):
    results = main.find(query, project)
    return results


def find_document(cik, project={"_id": 0}):
    result = main.find_one({"cik": cik}, project)
    return result


def search_filers(pipeline):
    cursor = main.aggregate(pipeline)
    return cursor


def search_filer(cik, project={"_id": 0}):
    cursor = main.aggregate(pipeline=[{"$match": {"cik": cik}}, {"$project": project}])
    try:
        result = cursor.next()
        return result
    except:
        return None


def add_filer(company):
    main.insert_one(company)


def edit_filer(query, value):
    main.update_one(query, value)


def delete_filer(cik):
    filer_query = {"cik": cik}
    logs.delete_one(filer_query)
    main.delete_one(filer_query)


def delete_filers(query):
    main.delete_many(query)


def create_log(value):
    logs.insert_one(value)


def find_log(cik, project={"_id": 0}):
    result = logs.find_one({"cik": cik}, project)
    return result


def find_specific_log(query):
    result = logs.find_one(query)
    return result


def add_log(cik, message, name="", identifier=""):
    if type(message) == dict:
        log_string = (
            f'{message["message"]}, ({message["name"]}) ({message["identifier"]})'
        )
        logs.update_one({"cik": cik}, {"$push": {"logs": log_string}})
    else:
        logs_string = [f"{log} ({name}) ({identifier})" for log in message.split("\n")]
        logs.update_one({"cik": cik}, {"$push": {"logs": {"$each": logs_string}}})


def add_logs(cik, formatted_logs):
    logs_split = []
    for formatted_log in formatted_logs:
        logs_split.extend(
            [
                f"{log_message} ({formatted_log['name']}) ({formatted_log['identifier']})"
                for log_message in formatted_log["message"].split("\n")
            ]
        )

    logs.update_one({"cik": cik}, {"$push": {"logs": {"$each": logs_split}}})


def edit_log(cik, stamp):
    logs.update_one({"cik": cik}, {"$set": stamp})


def edit_specific_log(query, value):
    logs.update_one(query, value)


def search_logs(pipeline):
    cursor = logs.aggregate(pipeline)
    return cursor


def delete_logs(query):
    logs.delete_many(query)


def edit_status(cik, status):
    logs.update_one({"cik": cik}, {"$set": {"status": status}})


def find_logs(project={"_id": 0}):
    result = logs.find(project)

    return result


def watch_logs(pipeline):
    cursor = main.watch(pipeline)
    return cursor


def add_query_log(cik, query):
    try:
        filer_done = find_filer(cik, {"cik": 1, "name": 1, "_id": 0, "filings": 1})
        filer_log = find_log(cik)
        if filer_done and filer_log:

            stock_count = 0
            filings = filer_done["filings"]
            for access_number in filings:
                filing_stocks = filings[access_number].get("stocks", [])
                for _ in filing_stocks:
                    stock_count += 1

            query_log = {
                **filer_done,
                "log": filer_log,
                "count": stock_count,
                "type": query,
                "timestamp": datetime.now().timestamp(),
            }
            statistics.insert_one(query_log)
    except Exception as e:
        logging.error(e)


# def search_sec(pipeline):
#     cursor = companies.aggregate(pipeline)
#     return cursor


logging.info("[ Database (MongoDB) Initialized ]")
