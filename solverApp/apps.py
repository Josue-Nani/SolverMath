from django.apps import AppConfig

class SolverappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'solverApp'

    def ready(self):
        import solverApp.signals
