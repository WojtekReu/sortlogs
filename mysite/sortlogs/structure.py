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
            v for k, v in cls.__dict__.items() if not k.startswith('_') and isinstance(v, str)
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
    LOG = 'log'
    INFO = 'info'
    ERROR = 'error'
    WARN = 'warn'


class Category(BasicStructure):
    """
    Main structure element
    """
    NGINX = 'nginx'
    UWSGI = 'uwsgi'
    CELERY = 'celery'
    MAIL = 'mail'


class Domain(BasicStructure):
    """
    Domain pmno was earlier zgloszenia
    """
    PMNO = 'pmno'
    ZGLOSZENIA = 'zgloszenia'
    TESTPMNO = 'testpmno'
    SPORT = 'sport'


class Port(BasicStructure):
    """
    Only Category.NGINX has ports
    """
    HTTPS = '443'
    WWW = '80'
    EMPTY = ''


# first part of filename
INPUT_FILES = {
    'pmno.pl-443-access': (Level.LOG, Category.NGINX, Domain.PMNO, Port.HTTPS),
    'pmno.pl-443-error': (Level.ERROR, Category.NGINX, Domain.PMNO, Port.HTTPS),
    'pmno.pl-80-access': (Level.LOG, Category.NGINX, Domain.PMNO, Port.WWW),
    'pmno.pl-80-error': (Level.ERROR, Category.NGINX, Domain.PMNO, Port.WWW),
    'sport.reu.pl-443-access': (Level.LOG, Category.NGINX, Domain.SPORT, Port.HTTPS),
    'sport.reu.pl-443-error': (Level.ERROR, Category.NGINX, Domain.SPORT, Port.HTTPS),
    'sport.reu.pl-80-access': (Level.LOG, Category.NGINX, Domain.SPORT, Port.WWW),
    'sport.reu.pl-80-error': (Level.ERROR, Category.NGINX, Domain.SPORT, Port.WWW),
    'test-pmno.reu.pl-443-access': (Level.LOG, Category.NGINX, Domain.TESTPMNO, Port.HTTPS),
    'test-pmno.reu.pl-443-error': (Level.ERROR, Category.NGINX, Domain.TESTPMNO, Port.HTTPS),
    'test-pmno.reu.pl-80-access': (Level.LOG, Category.NGINX, Domain.TESTPMNO, Port.WWW),
    'test-pmno.reu.pl-80-error': (Level.ERROR, Category.NGINX, Domain.TESTPMNO, Port.WWW),
    'zgloszenia-pmno.reu.pl-443-access': (Level.LOG, Category.NGINX, Domain.ZGLOSZENIA, Port.HTTPS),
    'zgloszenia-pmno.reu.pl-443-error': (Level.ERROR, Category.NGINX, Domain.ZGLOSZENIA, Port.HTTPS),
    'zgloszenia-pmno.reu.pl-80-access': (Level.LOG, Category.NGINX, Domain.ZGLOSZENIA, Port.WWW),
    'zgloszenia-pmno.reu.pl-80-error': (Level.ERROR, Category.NGINX, Domain.ZGLOSZENIA, Port.WWW),
    'pmnopl-stdout---supervisor': (Level.LOG, Category.UWSGI, Domain.PMNO, Port.EMPTY),
    'pmnopl-celery-stdout---supervisor': (Level.LOG, Category.CELERY, Domain.PMNO, Port.EMPTY),
    'sportex-stdout---supervisor': (Level.LOG, Category.UWSGI, Domain.SPORT, Port.EMPTY),
    'sportex-celery-stdout---supervisor': (Level.LOG, Category.CELERY, Domain.SPORT, Port.EMPTY),
    'testpmno-stdout---supervisor': (Level.LOG, Category.UWSGI, Domain.TESTPMNO, Port.EMPTY),
    'testpmno-celery-stdout---supervisor': (Level.LOG, Category.CELERY, Domain.TESTPMNO, Port.EMPTY),
    'zgpmno-stdout---supervisor': (Level.LOG, Category.UWSGI, Domain.ZGLOSZENIA, Port.EMPTY),
    'mail.err': (Level.ERROR, Category.MAIL, Domain.PMNO, Port.EMPTY),
    'mail.log': (Level.LOG, Category.MAIL, Domain.PMNO, Port.EMPTY),
    'mail.warn': (Level.WARN, Category.MAIL, Domain.PMNO, Port.EMPTY),
    'mail.info': (Level.INFO, Category.MAIL, Domain.PMNO, Port.EMPTY),
}
