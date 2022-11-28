Sortlogs
========

This repo contains two commands:

Command add_data_to_logs.py writes date to first place every line with date.

	./add_date_to_logs.py mail.err.1.gz

Command rename_logs.py change filenames for many logfiles according pattern.

    ./rename_logs.py access.log

Use these commands with caution. You can overwrite your data using this commands.

Sortlogs
--------

This is Django module

Modify mysite.settings.py

Import logging and set logging level to INFO:

    import logging
    logging.basicConfig(level=logging.INFO)

Add configuration for redis connection in CACHES, use key "redis":

    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": "redis://127.0.0.1:6379/0",
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }
