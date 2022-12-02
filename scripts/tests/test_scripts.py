import pytest
import sys
from datetime import datetime

from .. import add_date_to_logs, rename_logs
from .prepare import (
    ExampleMailInfo,
    ExampleMailLogs,
    ExampleNginxLogs,
    MAIL_ERROR_DATA,
    MAIL_INFO_DATA,
)


def test_rename_logs():
    """
    Test command `./rename_logs.py example.com-443-access.log --destination=tmp_dest_files`
    """
    with ExampleNginxLogs() as example:
        # append required param for script to work properly
        sys.argv.append("./rename_logs.py")
        sys.argv.append("example.com-443-access.log")
        sys.argv.append("--destination=tmp_dest_files")

        try:
            rename_logs.typer.run(rename_logs.main)
        except SystemExit as e:
            assert e.code == 0

        assert example.result1.exists() is True
        assert example.result2.exists() is True


def test_add_date_to_logs():
    """
    Test command `./add_date_to_logs.py mail.err.01 --destination=tmp_dest_files`
    """
    with ExampleMailLogs() as example:
        # append required param for script to work properly
        sys.argv.append("./add_date_to_logs.py")
        sys.argv.append(str(example.input))
        sys.argv.append("--destination=tmp_dest_files")

        try:
            add_date_to_logs.typer.run(add_date_to_logs.main)
        except SystemExit as e:
            assert e.code == 0

        result = ""
        with open(example.result, "r") as f:
            for line in f.readlines():
                result += line

        # data with line reverse order
        input_data = ""
        for line in MAIL_ERROR_DATA.rstrip().split("\n"):
            input_data = f"{datetime.now().year} {line}\n" + input_data

        assert result == input_data


def test_add_date_to_logs_info_filename():
    """
    Test command `./add_date_to_logs.py mail.info.01 --destination=tmp_dest_files`
    """
    with ExampleMailInfo() as example:
        # append required param for script to work properly
        sys.argv.append("./add_date_to_logs.py")
        sys.argv.append(str(example.input))
        sys.argv.append("--destination=tmp_dest_files")

        try:
            add_date_to_logs.typer.run(add_date_to_logs.main)
        except SystemExit as e:
            assert e.code == 0

        result = ""
        with open(example.result, "r") as f:
            for line in f.readlines():
                result += line

        # data with normal line order
        input_data = ""
        for line in MAIL_INFO_DATA.rstrip().split("\n"):
            input_data += f"{datetime.now().year} {line}\n"

        assert result == input_data
