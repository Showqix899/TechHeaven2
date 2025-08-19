from django.apps import AppConfig


class ReviewConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'review'

    def ready(self):
        # Import signals to ensure they are registered
        import review.signals
