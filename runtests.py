#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


base_path = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")


default_test_apps = [
    'tests',
]


def runtests(*args):
    import django
    django.setup()

    from django.conf import settings, global_settings
    from django.core.management.commands.test import Command

    settings.STATICFILES_STORAGE = global_settings.STATICFILES_STORAGE

    test_command = Command()
    test_apps = list(args or default_test_apps)
    test_command.execute(verbosity=settings.TEST_VERBOSITY, *test_apps)


if __name__ == '__main__':
    runtests(*sys.argv[1:])
