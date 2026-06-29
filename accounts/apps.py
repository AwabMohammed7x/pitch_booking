from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        # بنقول ليه: اعمل import لملف الـ signals عشان حراس الإشارات يصحصحوا ويبدأوا يسمعوا
        import accounts.signals
