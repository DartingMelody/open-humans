import json

from django.contrib import messages as django_messages
from django.core.urlresolvers import reverse_lazy
from django.http import (HttpResponseRedirect, HttpResponseBadRequest,
                         HttpResponseNotFound, HttpResponse)
from django.views.generic import TemplateView, View

from social.apps.django_app.default.models import UserSocialAuth

from data_import.views import BaseDataRetrievalView

from .models import DataFile


class DataRetrievalView(BaseDataRetrievalView):
    """
    Initiate the RunKeeper data retrieval task.
    """

    datafile_model = DataFile

    def get_app_task_params(self, request):
        return request.user.runkeeper.get_retrieval_params()


class FinalizeImportView(TemplateView, DataRetrievalView):
    """
    Handle the finalization of the RunKeeper import process.
    """

    template_name = 'runkeeper/finalize-import.html'


class DisconnectView(View):
    """
    Delete any RunKeeper credentials the user may have.
    """

    @staticmethod
    def post(request):
        django_messages.success(request, (
            'You have cancelled your connection to RunKeeper.'))

        request.user.runkeeper.disconnect()

        return HttpResponseRedirect(reverse_lazy('my-member-research-data'))


class DeauthorizeView(View):
    """
    This view is called by RunKeeper any time a user deactivates their
    RunKeeper account.
    """

    @staticmethod
    def post(request):
        try:
            data = json.loads(request.body)
        except ValueError:
            return HttpResponseBadRequest()

        if 'access_token' not in data:
            return HttpResponseBadRequest()

        try:
            user_social_auth = UserSocialAuth.objects.get(
                provider='runkeeper',
                extra_data__contains='"access_token": "{}"'.format(
                    data['access_token']))
        except UserSocialAuth.DoesNotExist:
            return HttpResponseNotFound()

        user = user_social_auth.user

        if 'delete_health' in data and data['delete_health']:
            user.runkeeper.datafiles.all().delete()

        user.runkeeper.disconnect()

        return HttpResponse()