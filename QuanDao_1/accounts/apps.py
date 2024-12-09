from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'QuanDao_1.accounts'

    def ready(self):
        import QuanDao_1.accounts.signals
        import QuanDao_1.academy.signals
