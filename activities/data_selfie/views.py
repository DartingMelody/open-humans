from django.apps import apps
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.views.generic.base import View
from django.views.generic.edit import DeleteView, UpdateView
from django.views.generic.list import ListView

from s3upload.views import DropzoneS3UploadFormView

from common.mixins import PrivateMixin
from data_import.models import DataFile
from data_import.utils import get_upload_dir, get_upload_dir_validator

from . import label
from .forms import DataSelfieUpdateViewForm
from .models import DataSelfieDataFile


class UploadView(PrivateMixin, DropzoneS3UploadFormView):
    """
    Allow the user to upload a data selfie file.
    """

    template_name = 'data_selfie/upload.html'
    success_url = reverse_lazy('activities:data-selfie:manage')

    def get_upload_to(self):
        return get_upload_dir(DataSelfieDataFile, self.request.user)

    def get_upload_to_validator(self):
        return get_upload_dir_validator(DataSelfieDataFile, self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UploadView, self).get_context_data(**kwargs)

        context.update({
            'app': apps.get_app_config(label),
        })

        return context

    def form_valid(self, form):
        """
        Save the uploaded DataFile.
        """
        data_file = DataSelfieDataFile(file=form.cleaned_data.get('key_name'),
                                       user=self.request.user,
                                       source='data_selfie')
        data_file.save()

        return super(UploadView, self).form_valid(form)


class DataSelfieView(PrivateMixin, ListView):
    """
    Creates a view for displaying data selfie files.
    """

    template_name = 'data_selfie/manage.html'
    context_object_name = 'data_files'

    def get_queryset(self):
        return DataSelfieDataFile.objects.filter(user=self.request.user)


class DataSelfieAcknowledgeView(PrivateMixin, View):
    """
    Let the user acknowledge that they've seen the data selfie modal.
    """

    @staticmethod
    def post(request):
        user_data = request.user.data_selfie
        user_data.seen_page = True
        user_data.save()

        return HttpResponse('')


class DataSelfieUpdateView(PrivateMixin, UpdateView):
    """
    Creates a view for displaying data selfie files.
    """

    form_class = DataSelfieUpdateViewForm
    model = DataFile
    template_name = 'data_selfie/edit.html'
    success_url = reverse_lazy('activities:data-selfie:manage')

    def get_object(self, queryset=None):
        return (DataSelfieDataFile.objects.get(id=self.kwargs['data_file'],
                                               user=self.request.user))


class DataSelfieFileDeleteView(PrivateMixin, DeleteView):
    """
    Let the user delete a data selfie DataFile.
    """

    template_name = 'data_selfie/file-delete.html'
    success_url = reverse_lazy('activities:data-selfie:manage')

    def get_object(self, queryset=None):
        return DataSelfieDataFile.objects.get(id=self.kwargs['data_file'],
                                              user=self.request.user)
