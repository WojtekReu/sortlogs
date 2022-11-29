from datetime import datetime
import re
from typing import Optional


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
