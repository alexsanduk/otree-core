# -*- coding: utf-8 -*-
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, Http404, HttpResponseNotFound
import vanilla
import otree.constants as constants
from otree.sessionlib.models import Session
from otree.session import create_session, SessionTypeDirectory
import threading
import time
import urllib
from otree.common import get_session_module, get_models_module, app_name_format
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from otree.views.demo import escaped_start_link_url, info_about_session_type
from otree import forms
from django.core.urlresolvers import reverse

@user_passes_test(lambda u: u.is_staff)
@login_required
class SessionTypes(vanilla.View):

    @classmethod
    def url_pattern(cls):
        return r'^session_types/$'

    def get(self, *args, **kwargs):

        session_types_info = []
        for session_type in SessionTypeDirectory().select():
            session_types_info.append(
                {
                    'type_name': session_type.name,
                    'url': escaped_start_link_url(session_type.name),
                    'doc': session_type.doc or '',
                    'subsession_apps': ', '.join([app_name_format(app_name) for app_name in session_type.subsession_apps]),
                }
            )
        return render_to_response('otree/admin/session_types.html', {'session_types_info': session_types_info})

class CreateSessionForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.session_type = kwargs.pop('session_type')
        super(CreateSessionForm, self).__init__(*args, **kwargs)

    num_participants = forms.IntegerField()
    base_pay = forms.MoneyField()

    def clean_num_participants(self, cleaned_data):
        lcm = self.session_type.lcm()
        if not cleaned_data['num_participants'] % lcm:
            raise ValueError('Number of participants must be a multiple of {}'.format(lcm))


@user_passes_test(lambda u: u.is_staff)
@login_required
class CreateSession(vanilla.FormView):

    @classmethod
    def url_pattern(cls):
        return r"^admin/session_type/(?P<session_type>.+)/create$"

    def dispatch(self, request, *args, **kwargs):
        session_type_name=urllib.unquote_plus(kwargs['session_type'])
        self.session_type = SessionTypeDirectory().get_item(session_type_name)

    def get(self, *args, **kwargs):
        context = info_about_session_type(self.session_type)
        return render_to_response('otree/admin/CreateSession.html', context)

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['session_type'] = self.session_type
        return super(CreateSession, self).get_form(data, files, **kwargs)

    def form_valid(self, form):
        session = create_session(
            num_participants = self.request.POST['num_participants'],
            base_pay = self.request.POST['base_pay']
        )
        admin_url = reverse('admin:%s_%s_change' % (session._meta.app_label, session._meta.module_name), args=(session.pk,))
        return HttpResponseRedirect(admin_url)