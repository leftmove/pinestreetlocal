from fastapi import BackgroundTasks, APIRouter, HTTPException
from fastapi.responses import FileResponse

import os
import json

from .utils import database
from .utils.cache import cache
from .utils.backup import backup_collections
from .utils.analysis import end_dangling

from .filer import create_filer_try


router = APIRouter(
    tags=["general"],
)


@router.on_event("startup")
async def startup():
    end_dangling()


@cache(24)
@router.get("/", status_code=200)
async def info():
    return {"message": "Hello World!"}


@cache
@router.get("/undefined", status_code=200)
async def info_undefined():
    return {"message": "Hello World!"}


@cache
@router.get("/backup", status_code=200)
async def backup(password: str, background: BackgroundTasks):
    if password != os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(detail="Unable to give access.", status_code=403)

    background.add_task(backup_collections)
    return {"message": "Backup started."}


@cache(1)
@router.get("/query", status_code=200, include_in_schema=False)
async def query_top(password: str, background: BackgroundTasks):
    if password != os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(detail="Unable to give access.", status_code=403)

    type_query = {"type": "query"}
    restore_log = database.find_specific_log(type_query)
    if restore_log:
        status = restore_log["status"]
        if status == "running":
            raise HTTPException(status_code=429, detail="Restore already running.")
        else:
            database.edit_specific_log(type_query, {"$set": {"status": "running"}})
    else:
        database.create_log({**type_query, "status": "running"})

    with open("./public/searched.json") as t:
        filer_ciks = json.load(t)
    with open("./public/top.json") as t:
        filer_ciks.extend(json.load(t))

    def cycle_filers(ciks):
        for cik in ciks:
            create_filer_try(cik)
        database.edit_specific_log(type_query, {"$set": {"status": "stopped"}})

    background.add_task(cycle_filers, filer_ciks)

    return {"description": "Started querying filers."}


@cache(1)
@router.get("/restore", status_code=200)
async def progressive_restore(password: str, background: BackgroundTasks):
    if password != os.environ["ADMIN_PASSWORD"]:
        raise HTTPException(detail="Unable to give access.", status_code=403)

    type_query = {"type": "restore"}
    restore_log = database.find_specific_log(type_query)
    if restore_log:
        status = restore_log["status"]
        if status == "running":
            raise HTTPException(status_code=429, detail="Restore already running.")
        else:
            database.edit_specific_log(type_query, {"$set": {"status": "running"}})
    else:
        database.create_log({**type_query, "status": "running"})

    filers = database.find_filers({}, {"cik": 1})
    all_ciks = [filer["cik"] for filer in filers]

    def cycle_filers(ciks):
        for cik in ciks:
            database.delete_filer(cik)
            create_filer_try(cik)
        database.edit_specific_log(type_query, {"$set": {"status": "stopped"}})

    background.add_task(cycle_filers, all_ciks)

    return {"description": "Started progressive restore of filers."}


@cache
@router.get("/favicon.ico", status_code=200)
async def favicon():
    return FileResponse("./public/favicon.ico")