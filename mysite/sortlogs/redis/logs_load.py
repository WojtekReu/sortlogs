from datetime import datetime
import gzip
import json
import os
import pytz
import redis
import logging
from typing import Optional, Self, Callable

from django_redis import get_redis_connection

from ..parsers import celery_parser, mail_parser, nginx_err_parser, nginx_log_parser, uwsgi_parser
from ..structure import INPUT_FILES, Level, Category


BASE_DATES = "base_dates"  # set
BASE_FILES = "base_files"  # list
BASE_KEYS = "base_keys"  # hash
BASE_KEYS_LEN = "base_keys_len"  # hash: key = log_uwsgi_localhost__2022-09-20; value = 5690 (len)
# keys for BASE_KEY hash
FIRST_LOG_TIME = "first_log_time"  # time of the first log in the key
LAST_LOG_TIME = "last_log_time"  # time of the last log in the key
LINES_NUMBER = "lines_number"  # how many log lines has the key


class Redis:
    """
    Connection to redis db
    """

    def __init__(self) -> None:
        """
        Initialize connection to redis database
        """
        self.redis = get_redis_connection("default")


class LogParser:
    """
    Setup for log parser
    """

    def __init__(self, filename: str) -> None:
        """
        Set main log settings for loaded file
        """
        self.category: str
        self.level: str
        self.domain: str
        self.port: str
        self.is_key_changed: bool = False

        for filename_begin, matrix in INPUT_FILES.items():
            if filename.startswith(filename_begin):
                self.level = matrix[0]
                self.category = matrix[1]
                self.domain = matrix[2]
                self.port = matrix[3]
                self.parser = self.choose_parser_method()
                break
        else:
            raise ValueError(f"ERROR: File {filename} doesn't match to any INPUT_FILES keys.")

    def choose_parser_method(self) -> Callable:
        """
        Choose parser which will search date and time in any line of file
        """
        if self.category == Category.NGINX:
            if self.level == Level.LOG:
                return nginx_log_parser

            elif self.level == Level.ERROR:
                return nginx_err_parser

        elif self.category == Category.UWSGI:
            return uwsgi_parser

        elif self.category == Category.CELERY:
            return celery_parser

        elif self.category == Category.MAIL:
            return mail_parser

        raise ValueError(f"Specify parser for category {self.category} or level {self.level}")

    # def get_key_value(self, line: str):
    #     """
    #     Prepare key for redis db according to date
    #     """
    #     log_datetime = self.parser(line)
    #
    #     if self.first_log_time:
    #         key_date, log_time = self.get_date_time(line)
    #
    #     key = f'{self.level}_{self.category}_{self.domain}_{self.port}_{self.key_date}'
    #     if key != self.key_before:
    #         # any time when new key is generated then check if order is maintain
    #         if self.category == Category.UWSGI and line.startswith('*** Starting uWSGI '):
    #             self.correct_date_time()
    #
    #         self.is_key_changed = True
    #         self.key_before = key
    #         self.time_before = self.log_time
    #     return key, line


class LogLine:
    """
    Parsed line of logs
    """

    key: str = ""
    key_date: str = ""
    log_time: str = ""
    line: str = ""
    datetime: datetime

    def __init__(self, line: str) -> None:
        """
        Set parsed line
        """
        self.line = line

    def parse_line(self, log_parser: LogParser, log_line_before: Self) -> None:
        """
        Set self.datetime, self.key_date and self.log_time for this log_line
        """
        line_datetime = log_parser.parser(self.line)
        if line_datetime:
            self.datetime = line_datetime
            self.set_key_attrs()
            self.key = (
                f"{log_parser.level}_{log_parser.category}_{log_parser.domain}_"
                f"{log_parser.port}_{self.key_date}"
            )
        else:
            self.datetime = log_line_before.datetime
            self.key_date = log_line_before.key_date
            self.log_time = log_line_before.log_time
            self.key = log_line_before.key

    def correct_datetime(self) -> None:
        """
        Some log rows have time in local timezone. Change it to UTC
        """
        self.datetime = pytz.timezone("UTC").localize(self.datetime)
        warsaw_zone = pytz.timezone("Europe/Warsaw")
        self.key_date = self.datetime.astimezone(warsaw_zone).strftime("%Y-%m-%d")
        self.log_time = self.datetime.astimezone(warsaw_zone).strftime("%H:%M:%S")
        if not self.key.endswith(self.key_date):
            # change key if needed
            self.key = "_".join(self.key.split("_")[:-1] + [self.key_date])

    def set_key_attrs(self) -> None:
        """
        Set key_date and log_time
        """
        self.key_date = self.datetime.strftime("%Y-%m-%d")
        self.log_time = self.datetime.strftime("%H:%M:%S")


class Loader(Redis):
    """
    Main class load logs data to redis.
    """

    log_line_before: Optional[LogLine] = None
    temporary_key: Optional[str] = None
    first_log_time: str
    log_parser: LogParser

    def update_base_keys(self, log_line: LogLine) -> None:
        """
        Set to BASE_KEYS hash time first and last logs, and also lines number.
        """
        if log_line:
            # Update FIRST_LOG_TIME in redis hash
            key = log_line.key
            values = self.get_base_keys(key)

            if FIRST_LOG_TIME not in values or log_line.log_time < values[FIRST_LOG_TIME]:
                values[FIRST_LOG_TIME] = log_line.log_time
            self.set_base_keys(key, values)

        if self.log_line_before:
            # update LAST_LOG_TIME nad lines number in redis hash
            key = self.log_line_before.key
            values = self.get_base_keys(key)
            values[LAST_LOG_TIME] = self.log_line_before.log_time
            values[LINES_NUMBER] = self.calculate_logs_len(key)
            self.set_base_keys(key, values)

    def get_base_keys(self, key: str) -> dict[str]:
        """
        Get values from BASE_KEYS hash or empty dict
        """
        values_str = self.redis.hget(BASE_KEYS, key)
        if values_str:
            return json.loads(values_str)
        else:
            return {}

    def set_base_keys(self, key: str, values: dict) -> None:
        """
        Set BASE_KEYS values
        """
        values_str = json.dumps(values)
        self.redis.hset(BASE_KEYS, key, values_str)

    def calculate_logs_len(self, key: str) -> int:
        """
        Calculate how meny lines is in this key
        """
        return self.redis.llen(key)

    def load_file_logs(self, file_path_str: str) -> None:
        """
        Load file with logs and start processing filelog
        """
        file_path = os.path.join(os.getcwd(), file_path_str)
        filename = file_path_str.split("/")[-1]
        self.redis.rpush(BASE_FILES, filename)
        self.log_parser = LogParser(filename)

        if filename.endswith(".gz"):
            function_open = gzip.open
        else:
            function_open = open
        with function_open(file_path, "rt") as f:
            for line in f.readlines():
                log_line = LogLine(line)
                log_line.parse_line(self.log_parser, self.log_line_before)

                try:
                    if self.log_line_before.key != log_line.key:
                        self.check_order(log_line)
                        # any time when new key is generated then check if order is maintain
                        if self.temporary_key:
                            self.temporary_key_process(log_line)
                            self.temporary_key = ""
                        self.update_base_keys(log_line)
                except AttributeError:
                    # self.log_line_before is None
                    # first time set log_line_before
                    self.check_order(log_line)
                    self.update_base_keys(log_line)

                self.redis.rpush(log_line.key, log_line.line)
                self.redis.sadd(BASE_DATES, log_line.key_date)
                self.log_line_before = log_line

            if self.temporary_key:
                # check temporary_key for last key
                self.temporary_key_process(log_line)
            self.update_base_keys(log_line)

    def check_order(self, new_log_line: LogLine) -> None:
        """
        Logs order is required. If you try to load older logs than exists in specified key, then
        rename existing key to temporary name, load logs and check if you can join existing logs.
        """
        if self.log_parser.category == Category.UWSGI and new_log_line.line.startswith(
            "*** Starting uWSGI "
        ):
            new_log_line.correct_datetime()

        key = new_log_line.key
        log_time = new_log_line.log_time
        base_key = self.get_base_keys(key)
        if base_key.get(LAST_LOG_TIME) and log_time <= base_key.get(LAST_LOG_TIME):
            self.temporary_key = f"{key}_{log_time}"
            self.first_log_time = base_key.get(FIRST_LOG_TIME)  # this is needed later
            try:
                self.redis.rename(key, self.temporary_key)
            except redis.exceptions.ResponseError as e:
                logging.error("Some error for key: %s", key)
                raise e
            logging.warning(
                'Create temporary_key "%s" for key "%s"',
                self.temporary_key,
                key,
            )

    def temporary_key_process(self, log_line: LogLine) -> None:
        """
        If temporary key exists then try to move logs from temporary key to proper key.
        """
        if log_line.log_time < self.first_log_time:
            while True:
                value = self.redis.lpop(self.temporary_key)
                if value is None:
                    logging.info("Key joined to: %s", log_line.key)
                    break
                self.redis.rpush(log_line.key, value)
        else:
            logging.warning(
                'Logs still in temporary key: %s because "%s" >= "%s"',
                self.temporary_key,
                log_line.log_time,
                self.first_log_time,
            )


class LogsFromRedis(Redis):
    """
    Get logs from redis db
    """

    def get_keys(self, pattern: str) -> list[str]:
        """
        Get keys list
        """
        return sorted([key.decode("utf-8") for key in self.redis.keys(pattern)])

    def get_values(self, pattern: str) -> list[tuple[str, str]]:
        """
        Get list of tuple(key, value)
        """
        values = []
        for key in self.get_keys(pattern):
            for nr in range(self.redis.llen(key)):
                value = self.redis.lindex(key, nr).decode("utf-8")
                values.append(
                    (
                        key,
                        value,
                    )
                )
        return values

    def get_values_for_key(self, key: str, start: int = 0, end: int = -1) -> list[str]:
        """
        Get all values from list
        """
        return [value.decode("utf-8") for value in self.redis.lrange(key, start, end)]

    def del_all(self, pattern: str) -> None:
        """
        Delete all keys matched to pattern. Use this method with extra caution!
        """
        for key in self.get_keys(pattern):
            self.redis.delete(key)
            self.redis.hdel(BASE_KEYS, key)

    def calculate_all_logs_len(self) -> None:
        """
        Calculate number of lines in key and write it to BASE_KEYS_LEN.
        """
        for key in self.redis.smembers(BASE_KEYS):
            len_key = self.redis.llen(key)
            self.redis.hset(BASE_KEYS_LEN, key, len_key)

    def get_key_logs_number(self, key: str) -> tuple[str, str, str]:
        """
        Get info about key from BASE_KEYS
        """
        values_str = self.redis.hget(BASE_KEYS, key)
        if values_str is not None:
            values = json.loads(values_str)
            return (
                values.get(FIRST_LOG_TIME),
                values.get(LAST_LOG_TIME),
                values.get(LINES_NUMBER),
            )
        return (
            "",
            "",
            "",
        )
