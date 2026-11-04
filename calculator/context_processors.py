from .utils import get_settings


def settings_context(request):
    try:
        return {'active_settings': get_settings()}
    except Exception:
        # e.g. migrations have not been applied yet
        return {'active_settings': None}
