from django.apps import AppConfig


class MarketingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.marketing'
    verbose_name = 'Marketing'

    def ready(self):
        import apps.marketing.signals
