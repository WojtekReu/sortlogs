from datetime import datetime
import pytz
import re
from typing import Optional, Callable

from .structure import INPUT_FILES, Level, Category


def nginx_log_parser(line: str) -> datetime:
    """
    Logs from nginx log files
    """
    # ip, _, user = line.split(" ")[:3]
    # str_time = line.split(']')[0].split('[')[1]
    str_time = re.split("[\[\]]", line, 2)[1]
    # day, month_str, year, hour, minute, second, zone = re.split('[/: ]', str_time)
    return datetime.strptime(str_time, "%d/%b/%Y:%H:%M:%S %z")


def nginx_err_parser(line: str) -> datetime:
    """
    Parser for nginx error line
    """
    str_time = " ".join(line.split(" ", 2)[:2])
    return datetime.strptime(str_time, "%Y/%m/%d %H:%M:%S")


def uwsgi_parser(line: str) -> Optional[datetime]:
    """
    Parser for uwsgi line
    """
    line_list = re.split("[\[\]]", line, 4)
    try:
        str_time = line_list[3]
    except IndexError:
        try:
            str_time = line_list[1]
        except IndexError:
            str_time = ""
    try:
        return datetime.strptime(str_time, "%a %b %d %H:%M:%S %Y")
    except ValueError:
        return


def celery_parser(line: str) -> Optional[datetime]:
    """
    Parser for supervisor celery log line
    """
    line_list = re.split("[\[\],]", line, 2)
    try:
        str_time = line_list[1]
    except IndexError:
        str_time = ""

    try:
        return datetime.strptime(str_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return


def mail_parser(line: str) -> Optional[datetime]:
    """
    Parser for mail logs line
    """
    # line = '2019 Jun 4 06:36:43 server postfix/smtps/smtpd[2299]: log message'
    str_time = " ".join(re.split(" ", line, 4)[:4])
    if len(str_time) < 12:
        # that means date has double spaces ex.: line = '2019 Jun  4 06:36:43 server ...'
        str_time = " ".join(re.split(" ", line, 5)[:5])

    try:
        # str_time = '2019 Feb 23 06:24:09'
        return datetime.strptime(str_time, "%Y %b %d %H:%M:%S")
    except ValueError:
        return


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

    def get_collection_name(self):
        """
        Generate collection name for logs
        """
        return f"{self.level}_{self.category}_{self.domain}_{self.port}"

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


class LogLine:
    """
    Parsed line of logs
    """

    cache: bool = False
    has_date: bool = False
    update: bool = False
    key: str = ""
    key_date: str = ""
    log_time: str = ""
    line: str = ""
    line_update: Optional[str] = None
    datetime: datetime
    inserted_id = None

    def __init__(self, log_parser: LogParser) -> None:
        """
        Set parsed line
        """
        self.parse = log_parser.parser

    def parse_line(self, line: str) -> None:
        """
        Set self.datetime, self.key_date and self.log_time for this log_line
        """
        line_datetime = self.parse(line)
        if line_datetime:
            self.datetime = line_datetime
            self.line = line
            self.has_date = True
            if self.cache:
                self.update = True
        else:
            if self.line_update is None:
                self.line_update = "".join((self.line, line))
                self.line = ""
                self.cache = True
            else:
                self.line_update = "".join((self.line_update, line))
            self.has_date = False

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
