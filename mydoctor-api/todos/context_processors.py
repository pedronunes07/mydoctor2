from .utils import get_panel_url


def navigation_urls(request):
    return {
        'default_panel_url': get_panel_url(request.user),
    }
