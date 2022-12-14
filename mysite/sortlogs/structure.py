"""
This module is some kind of project confing
"""


class BasicStructure:
    @classmethod
    def get_values(cls):
        """
        Get values
        """
        return list(
            v for k, v in cls.__dict__.items() if not k.startswith("_") and isinstance(v, str)
        )

    @classmethod
    def gen_list_choices(cls):
        """
        Generate list items for selector field.
        """
        items = cls.get_values()
        return zip(items, items)


class Level(BasicStructure):
    """
    Log level
    """

    LOG = "log"
    INFO = "info"
    ERROR = "error"
    WARN = "warn"


class Category(BasicStructure):
    """
    Main structure element
    """

    NGINX = "nginx"
    UWSGI = "uwsgi"
    CELERY = "celery"
    MAIL = "mail"


class Domain(BasicStructure):
    """
    Domains
    """

    EXAMPLE = "example"  # example.com
    TEST = "test"  # test.example.com


class Port(BasicStructure):
    """
    Only category NGINX has ports
    """

    HTTPS = "443"
    WWW = "80"
    EMPTY = ""


# first part of filename
INPUT_FILES = {
    "example.com-443-access": (Level.LOG, Category.NGINX, Domain.EXAMPLE, Port.HTTPS),
    "example.com-443-error": (Level.ERROR, Category.NGINX, Domain.EXAMPLE, Port.HTTPS),
    "example.com-80-access": (Level.LOG, Category.NGINX, Domain.EXAMPLE, Port.WWW),
    "example.com-80-error": (Level.ERROR, Category.NGINX, Domain.EXAMPLE, Port.WWW),
    "test.example.com-443-access": (Level.LOG, Category.NGINX, Domain.TEST, Port.HTTPS),
    "example-com-stdout---supervisor": (Level.LOG, Category.UWSGI, Domain.EXAMPLE, Port.EMPTY),
    "example-com-celery---supervisor": (Level.LOG, Category.CELERY, Domain.EXAMPLE, Port.EMPTY),
    "mail.err": (Level.ERROR, Category.MAIL, Domain.EXAMPLE, Port.EMPTY),
    "mail.log": (Level.LOG, Category.MAIL, Domain.EXAMPLE, Port.EMPTY),
    "mail.warn": (Level.WARN, Category.MAIL, Domain.EXAMPLE, Port.EMPTY),
    "mail.info": (Level.INFO, Category.MAIL, Domain.EXAMPLE, Port.EMPTY),
}
