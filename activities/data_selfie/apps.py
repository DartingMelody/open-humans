from common.app_configs import BaseConnectionAppConfig


class DataSelfieConfig(BaseConnectionAppConfig):
    """
    Configure the data selfie activity application.

    Note: The verbose_name matches the name of the 'provider' defined for this
    activity's authentication backend, as used by python-social-auth. For this
    activity, the backend is defined in common/oauth_backends.py
    """
    name = __package__
    verbose_name = 'Data selfie'

    disconnectable = False
    individual_deletion = True

    connection_template = 'data_selfie/activity.html'

    data_description = {
        'name': 'User-uploaded files',
        'description': 'Diverse data from user-uploaded files.',
    }
