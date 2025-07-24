from django.apps import AppConfig


class UserAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user_app'
    # [Az] to activate the signal in signals.py to creat main area
    def ready(self):
        import user_app.signals  # 👈 this line activates your signal
