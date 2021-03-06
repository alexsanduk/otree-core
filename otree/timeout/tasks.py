#!/usr/bin/env python
# -*- coding: utf-8 -*-

import django.test

from celery import shared_task

from otree import constants_internal


@shared_task
def submit_expired_url(url):

    client = django.test.Client()
    client.post(url, data={constants_internal.auto_submit: True}, follow=True)


@shared_task
def ensure_pages_visited(participant_pk_set, wait_page_index):

    """
    This is necessary when a wait page is followed by a timeout page.
    We can't guarantee the user's browser will properly continue to poll
    the wait page and get redirected, so after a grace period we load the page
    automatically, to kick off the expiration timer of the timeout page.

    """

    from otree.models.participant import Participant
    client = django.test.Client()

    unvisited_participants = Participant.objects.filter(
        pk__in=participant_pk_set,
        _index_in_pages__lte=wait_page_index,
    )

    for participant in unvisited_participants:
        # if the wait page is the first page,
        # then _current_form_page_url could be null.
        # in this case, use the start_url() instead,
        # because that will redirect to the current wait page.
        # (alternatively we could define _current_page_url or
        # current_wait_page_url)
        url = participant._current_form_page_url or participant._start_url()
        client.get(url, follow=True)
