"""
Prepare files for testing scripts
"""
import gzip
from pathlib import Path
import os
import sys
from typing import Self

MAIL_ERROR_DATA = """Dec 22 20:42:07 mailserver.example.com opendkim[1005]: Some error
Dec 22 18:10:01 mailserver.example.com opendkim[1005]: Another error occured
"""
MAIL_INFO_DATA = """Jan  8 06:25:20 mailserver.example.com postfix/smtpd[123]: warning: not known
Jan  8 06:25:21 mailserver.example.com postfix/smtpd[123]: connect from unknown
Jan  8 06:25:34 mailserver.example.com postfix/smtpd[123]: timeout after EHLO from unknown
"""
TMP_DEST_FILES = "tmp_dest_files"


def check_and_remove(path: Path) -> None:
    """
    Remove file if exists
    """
    if path.exists():
        os.remove(path)


class ArgvCache:
    """
    Manage sys.argv params
    """

    def __init__(self) -> None:
        """
        Initialize cache for sys.argv params
        """
        self.argv_data = []

    def cache_argv(self) -> None:
        """
        Remove command params from sys.argv because these params are delver to tested script and
        cause an error
        """
        self.argv_data = []
        while len(sys.argv):
            self.argv_data.append(sys.argv.pop())

    def restore_argv(self) -> None:
        """
        Clear sys.argv and restore origin argv params
        """
        sys.argv.clear()
        while len(self.argv_data):
            sys.argv.append(self.argv_data.pop())


class ExampleNginxLogs(ArgvCache):
    """
    Ensure files are removed and sys.argv unchanged after end of test
    """

    def __init__(self) -> None:
        """
        Initialize argv cache
        """
        super().__init__()
        self.input1 = Path("example.com-443-access.log.0")
        self.input2 = Path("example.com-443-access.log.1.gz")
        self.result1 = Path("tmp_dest_files/example.com-443-access.log.1000.gz")
        self.result2 = Path("tmp_dest_files/example.com-443-access.log.1001.gz")

    def __enter__(self) -> Self:
        """
        Create files for testing script and clear old results if exists
        """
        check_and_remove(self.result1)
        check_and_remove(self.result2)
        self.cache_argv()
        with open(self.input1, "wt") as f:
            f.write("Some example logs")

        with gzip.open(self.input2, "wt") as f:
            f.write("Some compressed example logs")

        return self

    def __exit__(self, *args) -> None:
        """
        Delete the files that were created as a result of running the script
        """
        self.restore_argv()
        check_and_remove(self.input1)
        check_and_remove(self.input2)
        check_and_remove(self.result1)
        check_and_remove(self.result2)


class ExampleMailLogs(ArgvCache):
    """
    For testing add_date_to_logs script ensure files are remove and sys.argv restored to initial
    values. This is case for processing error logs.
    """

    def __init__(self) -> None:
        """
        Initialize argv cache and input path
        """
        super().__init__()
        self.input = Path("mail.err.01")
        self.result = Path("tmp_dest_files/mail.err.01")
        self.mail_log_data = MAIL_ERROR_DATA

    def __enter__(self) -> Self:
        """
        Create files for testing script and clear old results if exists
        """
        check_and_remove(self.result)
        # create files for testing
        self.cache_argv()
        with open(self.input, "wt") as f:
            f.write(self.mail_log_data)

        return self

    def __exit__(self, *args) -> None:
        """
        Delete the files that were created as a result of running the script
        """
        self.restore_argv()
        check_and_remove(self.input)
        check_and_remove(self.result)


class ExampleMailInfo(ExampleMailLogs):
    """
    For testing add_date_to_logs script ensure files are remove and sys.argv restored to initial
    values. This is case for processing info logs.
    """

    def __init__(self) -> None:
        """
        Initialize argv cache and input path
        """
        super().__init__()
        self.input = Path("mail.info.01")
        self.result = Path("tmp_dest_files/mail.info.01")
        self.mail_log_data = MAIL_INFO_DATA
