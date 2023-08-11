"""
Load logs to storage
"""
from django.core.management.base import BaseCommand

from ...mongo.logs_load import Loader
import logging


class Command(BaseCommand):
    help = "Load logs to storage"

    def add_arguments(self, parser):
        parser.add_argument(
            "--logs-file",
            dest="logs_file",
            default=False,
            help="File with logs",
        )

    def handle(self, *args, **options):
        """
        Run command for logs loading
        """
        logs_file = options["logs_file"]
        Loader().load_file_logs(logs_file)
        logging.info("Loaded to db file: %s", logs_file)
