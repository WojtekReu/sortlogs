#!/usr/bin/python3
"""
Gzip and rename log files in order that was changed (by mtime).
./rename_logs.py example.com-443-access.log
"""
import logging
import os
from itertools import count
from pathlib import Path
import subprocess
import typer

# files in this directory can be overwritten.
DIRECTORY_DEST: str = "converted_logs"
FIRST_FILENAME_NUMBER: int = 1000
EXT: str = ".gz"

logging.basicConfig(level=logging.INFO)


def main(
    base_filename: str = typer.Argument(
        ...,
        help="unchanged file part",
    ),
    destination: Path = typer.Option(
        DIRECTORY_DEST,
        help="dir destination where move renamed file",
        exists=True,
        dir_okay=True,
        file_okay=False,
    ),
):
    """
    Rename and gzip files from current dir and move them to a new destination. Destination has to
    exist. Gzip file only if not gzipped.
    """
    listdir: list[str] = os.listdir(".")
    listdir = list(filter(lambda x: x.startswith(base_filename), listdir))
    listdir_ext: list = []
    for filename in listdir:
        mktime = os.stat(filename).st_mtime
        listdir_ext.append((filename, mktime))

    listdir_ext.sort(key=lambda x: x[1])
    counter = count(FIRST_FILENAME_NUMBER)
    destination_path = None

    for line in listdir_ext:
        filename = line[0]
        if filename.endswith(EXT):
            filename_gzipped = filename
        else:
            # use system gzip command to gzip file
            subprocess.check_call(["gzip", filename])
            # Note that unix gzip command rename file it is command gzip adds .gz to filename.
            # When command asks you about overwrite file then chose no, move renamed files again
            # to current directory and run process again.
            filename_gzipped = f"{filename}{EXT}"

        new_filename = f"{base_filename}.{next(counter)}{EXT}"
        destination_path = destination.joinpath(new_filename)

        while destination_path.exists():
            new_filename = f"{base_filename}.{next(counter)}{EXT}"
            destination_path = destination.joinpath(new_filename)

        os.rename(filename_gzipped, destination_path)
        logging.info(f"{filename} \t-> {destination_path}")

    if FIRST_FILENAME_NUMBER == next(counter):
        logging.info(f"Didn't find any files to rename for {base_filename}.")
    else:
        logging.info(f"The last renamed file is {destination_path}.")


if __name__ == "__main__":
    typer.run(main)
