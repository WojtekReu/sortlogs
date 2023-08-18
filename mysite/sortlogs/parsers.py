from datetime import datetime
import pytz
import re
from typing import Any, Optional

from .structure import INPUT_FILES, Level, Category

def choose_parser(filename: str, file_modified_date: datetime) -> Any:
    for filename_begin, matrix in INPUT_FILES.items():
        if filename.startswith(filename_begin):
            m = {
                "level": matrix[0],
                "category": matrix[1],
                "domain": matrix[2],
                "port": matrix[3],
            }
            if m["category"] == Category.NGINX:
                if m["level"] == Level.LOG:
                    return NginxLogParser(**m)

                elif m["level"] == Level.ERROR:
                    return NginxErrParser(**m)

            elif m["category"] == Category.UWSGI:
                return UwsgiParser(**m)

            elif m["category"] == Category.CELERY:
                return CeleryParser(**m)

            elif m["category"] == Category.MAIL:
                m["year"] = file_modified_date.year
                return MailParser(**m)

            elif m["category"] == Category.PG:
                return PostgresParser(**m)

            elif m["category"] == Category.REDIS:
                return RedisParser(**m)

            elif m["category"] == Category.SUPERVISORD:
                return SupervisordParser(**m)

    else:
        raise ValueError(f"ERROR: File {filename} doesn't match to any INPUT_FILES keys.")


class BaseLogParser:
    """
    Any log parser required at least datetime_format specified.
    """
    datetime_format = ""

    def __init__(self, **kwargs) -> None:
        """
        Set params
        """
        self.category: str = kwargs.get("category")
        self.level: str = kwargs.get("level")
        self.domain: str = kwargs.get("domain")
        self.port: str = kwargs.get("port")

    def parse_line(self, line: str) -> Optional[datetime]:
        """
        Parse line and get datetime. Line example:
        2021-09-09 21:23:43,286 INFO RPC interface 'supervisor' initialized
        """
        return self.get_date(" ".join(line.split(" ", 2)[:2]))

    def get_date(self, line: str) -> Optional[datetime]:
        """
        Get date and time from string
        """
        try:
            return datetime.strptime(line, self.datetime_format)
        except ValueError as e:
            return

    def get_collection_name(self):
        """
        Generate collection name for logs
        """
        return f"{self.level}_{self.category}_{self.domain}_{self.port}"


class NginxLogParser(BaseLogParser):
    """
    Parse nginx logs. Date is like this:
    "16/Feb/2020:06:24:23 +0000"
    """
    datetime_format = "%d/%b/%Y:%H:%M:%S %z"

    # ip, _, user = line.split(" ")[:3]
    # str_time = line.split(']')[0].split('[')[1]
    # day, month_str, year, hour, minute, second, zone = re.split('[/: ]', str_time)

    def parse_line(self, line: str) -> Optional[datetime]:
        """
        Parse line and get datetime for line like this:
        1.2.3.4 - - [16/Feb/2020:06:24:23 +0000] "GET /index.html HTTP/1.1" 200 191 "-" ...
        """
        return self.get_date(re.split("[\[\]]", line, 2)[1])


class NginxErrParser(BaseLogParser):
    """
    Parse nginx errors. Date is like this:
    "2020/6/30 06:24:53"
    """
    datetime_format = "%Y/%m/%d %H:%M:%S"


class UwsgiParser(BaseLogParser):
    """
    Parse uwsgi logs from supervisor.
    "Wed May 20 19:08:35 2020"
    """
    datetime_format = "%a %b %d %H:%M:%S %Y"

    def parse_line(self, line: str) -> Optional[datetime]:
        """
        Parse uwsgi logs from supervisor. The lines can be without date or some like this:
        *** Starting uWSGI 2.0.18 (64bit) on [Wed May 20 19:08:35 2020] ***
        [pid: 28593|app: 0|req: 1/1] 1.2.3.4 () {52 vars ...} [Wed May 20 22:36:02 2020] GET / ...
        """
        line_list = re.split("[\[\]]", line, 4)
        try:
            str_time = line_list[3]
        except IndexError:
            try:
                str_time = line_list[1]
            except IndexError:
                str_time = ""

        return self.get_date(str_time)

class CeleryParser(BaseLogParser):
    """
    Parser for supervisor celery log line
    "2019-06-03 03:41:18,934"
    """
    datetime_format = "%Y-%m-%d %H:%M:%S,%f"

    def parse_line(self, line:str) -> Optional[datetime]:
        """
        Parse celery logs from supervisor. Separators are `[`, `]`, `: ` (space after colon)
        [2019-06-03 03:41:18,934: ERROR/MainProcess] consumer: Cannot connect to redis://:**@localhost:6379/1:
        """
        line_list = re.split("[\[\]|: ]", line, 2)
        try:
            str_time = line_list[1]
        except IndexError:
            str_time = ""

        return self.get_date(str_time)


class MailParser(BaseLogParser):
    """
    Parser for mail logs line
    "2019 Jun  4 06:36:43"
    """
    datetime_format = "%Y %b %d %H:%M:%S"

    def __init__(self, **kwargs):
        """
        Year from file stat (mtime)
        """
        super().__init__(**kwargs)
        self.year = kwargs.get('year')

    def parse_line(self, line: str) -> Optional[datetime]:
        """
        Line usually don't have year value, but it can be added by script add_date_to_logs.py
        """
        # line = '2019 Jun 14 06:36:43 server postfix/smtps/smtpd[2299]: log message'
        # line = '2019 Jun  4 06:36:43 server ...'
        # line = 'Jun 4 06:36:43 server ...'
        if not line[:4].isdigit():
            line = f"{self.year} {line}"

        # line[:20] is '2019 Feb 23 06:24:09'
        return self.get_date(line[:20])


class PostgresParser(BaseLogParser):
    """
    Postgress server logs
    "2021-09-02 17:23:40.866 UTC"
    """
    datetime_format = "%Y-%m-%d %H:%M:%S.%f %Z"

    def parse_line(self, line: str) -> Optional[datetime]:
        """
        Get 3 datetime parts from begin of line separated by space.
        """
        return self.get_date(" ".join(line.split(" ", 3)[:3]))


class RedisParser(BaseLogParser):
    """
    Redis server logs
    "28 Aug 2022 00:01:00.138"
    """
    datetime_format = "%d %b %Y %H:%M:%S.%f"

    def parse_line(self, line: str) -> Optional[datetime]:
        """
        Date is from second to fifth element space separated.
        710:M 28 Aug 2022 00:01:00.138 * Background saving terminated with success
        """
        return self.get_date(" ".join(line.split(" ", 5)[1:5]))


class SupervisordParser(BaseLogParser):
    """
    Datetime string example: "2021-09-09 21:23:43,286"
    """
    datetime_format = "%Y-%m-%d %H:%M:%S,%f"


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
    datetime: Optional[datetime] = None
    inserted_id = None

    def __init__(self, log_parser: Any) -> None:
        """
        Set SomeLogParser.parse_line for specified file logs line
        """
        self.parse_line = log_parser.parse_line

    def set_line(self, line: str) -> None:
        """
        Set self.datetime, self.key_date and self.log_time for this log_line
        """
        line_datetime = self.parse_line(line)
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
