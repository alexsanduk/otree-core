#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')  # noqa

from django.core.wsgi import get_wsgi_application
from whitenoise.django import DjangoWhiteNoise

application = get_wsgi_application()
application = DjangoWhiteNoise(application)
