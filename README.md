Sortlogs
========

This repo contains two commands:

Command `add_data_to_logs.py` writes date to first place every line with date.

	./add_date_to_logs.py mail.err.1.gz

Command `rename_logs.py` change filenames for many logfiles according pattern.

    ./rename_logs.py access.log

Use these commands with caution. You can overwrite your data using this commands.

Sortlogs
--------

To use this module copy `sortlogs` from `mysite` to your Django project as module and modify 
`settings.py` and `urls.py`.

Add section which import logging and set logging level to INFO in `settings.py`:

    import logging
    logging.basicConfig(level=logging.INFO)

Customize admin index page in `YOUR_PROJECT/urls.py`:

    admin.site.index_template = "admin/custom_index.html"

Add this path to urlpatterns list in your project in `YOUR_PROJECT/urls.py`:

    path("admin/", include(("sortlogs.urls", "sortlogs"), namespace="sortlogs")),
