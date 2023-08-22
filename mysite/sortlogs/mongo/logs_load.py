import gzip
import os
from itertools import count
from datetime import datetime

import pymongo
from typing import Optional, Any
from django.conf import settings
from ..parsers import LogLine, choose_parser
from ..structure import (
    COLLECTION_NAME,
    FIRST_LOG_TIME,
    LAST_LOG_TIME,
    Level,
    LINES_NUMBER,
    LOADED_FILES,
)


class Database:
    """
    Connect to MongoDB
    """

    def __init__(self) -> None:
        """ """
        client = pymongo.MongoClient(settings.MONGODB_URI)
        self.db = client[settings.MONGODB_NAME]


class Loader(Database):
    """
    Main class load logs data to db.
    """

    log_line_before: Optional[LogLine] = None
    temporary_key: Optional[str] = None
    first_log_time: str

    def get_file_collections(self, filename: str) -> dict[str]:
        """
        Get information about file from db
        """
        return self.db[LOADED_FILES].find_one(
            {
                "filename": filename,
            }
        )

    def set_file_collections(self, values: dict) -> pymongo.results.InsertOneResult:
        """
        Set information about loaded file to db
        """
        return self.db[LOADED_FILES].insert_one(values)

    def check_file_collections(self, filename: str) -> bool:
        """
        Check if file exists in LOADED_FILES collection.
        """
        return bool(self.get_file_collections(filename))

    def update_file_collections(self, collection_id, values):
        """
        Update info about file in db
        """
        self.db[LOADED_FILES].find_one_and_update(
            filter={"_id": collection_id},
            update={"$set": values},
        )

    def calculate_logs_len(self, key: str) -> int:
        """
        Calculate how meny lines is in this key
        """
        return self.db.base_keys.count()

    def load_file_logs(self, file_path_str: str) -> None:
        """
        Load file with logs and start processing filelog
        """
        first_date = None
        file_path = os.path.join(os.getcwd(), file_path_str)
        filename = file_path_str.split("/")[-1]
        file_modified_date = datetime.utcfromtimestamp(os.stat(file_path).st_mtime)
        if self.check_file_collections(filename):
            pass  # raise Exception(f"The file '{filename}' has been previously uploaded.")

        insert_result = self.set_file_collections({"filename": filename})
        log_parser = choose_parser(filename, file_modified_date)
        log_collection = self.db[log_parser.get_collection_name()]

        log_line = LogLine(log_parser)

        if filename.endswith(".gz"):
            function_open = gzip.open
        else:
            function_open = open
        with function_open(file_path, "rt") as f:
            lines_counter = count()  # starts from 0
            for line in f.readlines():
                next(lines_counter)  # this is line_nr - 1
                log_line.set_line(line)

                if log_line.update:
                    self.update_log_line(log_collection, log_line)

                if log_line.has_date:
                    db_result = log_collection.insert_one(
                        {
                            "datetime": log_line.datetime,
                            "line": log_line.line,
                        }
                    )
                    log_line.inserted_id = db_result.inserted_id
                    if not first_date:
                        first_date = log_line.datetime

            if log_line.cache:
                self.update_log_line(log_collection, log_line)

            values = {
                FIRST_LOG_TIME: first_date,
                LAST_LOG_TIME: log_line.datetime,
                LINES_NUMBER: next(lines_counter),
                COLLECTION_NAME: log_parser.get_collection_name(),
            }
            self.update_file_collections(insert_result.inserted_id, values)

    def update_log_line(self, log_collection, log_line):
        log_collection.update_one(
            filter={"_id": log_line.inserted_id},
            update={
                "$set": {
                    "line": log_line.line_update,
                }
            },
        )
        log_line.line_update = None
        log_line.update = False
        log_line.cache = False


class LogsFromDb(Database):
    """
    Get logs from db
    """

    def get_logs(
        self, table_name: str, start_datetime: datetime, end_datetime: datetime, limit: int
    ) -> Any:
        """ """
        collection = (
            self.db[table_name]
            .find(
                {
                    "datetime": {"$gte": start_datetime, "$lte": end_datetime},
                }
            )
            .limit(limit)
        )
        return collection

    def get_tables(self) -> list[str]:
        """
        Get collection names from db filtered by Level
        """
        names = []
        for name in self.db.list_collection_names():
            for begin in Level.get_values():
                if name.startswith(f"{begin}_"):
                    names.append(name)
        return sorted(names)

    def get_loaded_files(self, table_name):
        """
        Get filenames and attrs from LOADED_FILES collection for specified table name.
        """
        collection = (
            self.db[LOADED_FILES]
            .find(
                {
                    "collection_name": table_name,
                }
            )
            .sort("filename", 1)
        )
        return collection
