#!/usr/bin/python3
"""
Gzip and rename log files in order that was changed (by mtime).
"""
import logging
import os
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
    listdir = os.listdir(".")
    listdir = list(filter(lambda x: x.startswith(base_filename), listdir))
    listdir_ext = []
    for filename in listdir:
        mktime = os.stat(filename).st_mtime
        listdir_ext.append((filename, mktime))

    listdir_ext.sort(key=lambda x: x[1])
    i = FIRST_FILENAME_NUMBER

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

        new_filename = f"{base_filename}.{i}{EXT}"
        destination_path = destination.joinpath(new_filename)

        if destination_path.exists():
            logging.warning(
                f"Destination file {destination_path} exists. Overwrite is not allowed."
            )
            raise typer.Abort()

        os.rename(filename_gzipped, destination_path)
        logging.info(f"{filename} \t-> {destination_path}")
        i += 1

    if i == FIRST_FILENAME_NUMBER:
        logging.info(f"Didn't find any files to rename for {base_filename}.")
    else:
        files_count = i - FIRST_FILENAME_NUMBER
        logging.info(f"For {base_filename} renamed {files_count} files.")


if __name__ == "__main__":
    typer.run(main)
