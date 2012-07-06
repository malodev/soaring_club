from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponseRedirect

def handle404 (view_function):
    """If we are not in debug mode, convert ObjectDoesNotExist to Http404"""
    def wrapper (*args, **kwargs):
        if not settings.DEBUG:
            try:
                return view_function (*args, **kwargs)
            except ObjectDoesNotExist:
                raise Http404
        else:
            return view_function (*args, **kwargs)
    return wrapper    
    