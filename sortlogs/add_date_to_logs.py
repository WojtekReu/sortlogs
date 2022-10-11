#!/usr/bin/python3
"""
Problem: Postfix mail logs do not have a year in any log line.
Solution: add year to beginning of each line in log file. The year is taken from mtime of the file.
Remember that year can be changed in the same file (ex. Dec -> Jan). Notice mail.err has reverse
chronological order.
"""
from datetime import datetime
import gzip
import os
from pathlib import Path
import typer

DIRECTORY_DEST = "corrected_mail_logs"


def get_month_from_line(line: str):
    """
    Get month from first word in the line, ex. Jan
    """
    month_str = line.split(" ", 1)[0]
    return datetime.strptime(month_str, "%b").month


def process_mail_err_file(f, f_dest, year: int):
    """
    Mail error logs have reverse chronology line - from newer to older
    """
    month_nr_before = 12
    file_data = []
    for line in f.readlines():
        month_nr = get_month_from_line(line)
        if month_nr > month_nr_before:
            year -= 1
            print(f"Year changed in mail.err: {year=}")
        month_nr_before = month_nr
        file_data.insert(0, f"{year} {line}")

    # write data from list to file
    for line in file_data:
        f_dest.write(line)


def process_mail_log_file(f, f_dest, years: list):
    """
    Process mail.log, mail.info and mail.warn files
    """
    month_nr_before = 1
    for line in f.readlines():
        # find if file has logs from more years than one. It means find Dec to Jan jumps.
        month_nr = get_month_from_line(line)
        if month_nr < month_nr_before:
            # year has changed
            # add to list older year: [2020] -> [2019, 2020]
            years.insert(0, years[0] - 1)
            print(f"Added to years list: {years=}")
        month_nr_before = month_nr

    f.seek(0)
    month_nr_before = 1
    year_index = 0
    year = years[year_index]
    # now you have years you want to write to new file
    for line in f.readlines():
        month_nr = get_month_from_line(line)
        if month_nr < month_nr_before:
            # get next year
            year = years[year_index]
            year_index += 1
            print(f"Year changed: {year=}  {year_index=}")
        # add year and write log line
        f_dest.write(f"{year} {line}")


def main(
    filename: Path = typer.Argument(
        ...,
        help="file with mail logs, can be text or gzipped file with .gz extension",
    ),
    destination: Path = typer.Option(
        DIRECTORY_DEST,
        help="dir destination where command create new file",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
):
    """
    Convert mail logs by adding year before each line with month name at first word.
    """
    years = []

    dest_file_path = destination.joinpath(filename)
    if dest_file_path.exists():
        print(
            f"ERROR: Destination file {dest_file_path} exists. Overwrite is not allowed."
        )
        raise typer.Exit(code=1)

    # Get year from input file mtime attribute.
    file_atime = os.stat(filename).st_atime
    file_mtime = os.stat(filename).st_mtime
    years.append(datetime.utcfromtimestamp(file_mtime).year)

    if str(filename).endswith(".gz"):
        # input file is gzipped ex. mail.info.1.gz
        function_open = gzip.open
    else:
        # input file is text file ex. mail.info
        function_open = open

    with function_open(filename, "rt") as f:
        with function_open(dest_file_path, "wt") as f_dest:
            if str(filename).startswith("mail.err"):
                process_mail_err_file(f, f_dest, years[0])
            else:
                process_mail_log_file(f, f_dest, years)

        os.utime(dest_file_path, (file_atime, file_mtime))


if __name__ == "__main__":
    typer.run(main)
