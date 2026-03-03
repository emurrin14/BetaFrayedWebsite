from django.shortcuts import redirect
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch

class DropPageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            protected_url = reverse('drop_page')
        except NoReverseMatch:
            return self.get_response(request)

        is_authorized = request.session.get('is_preview_authorized', False)
        path = request.path
        
        if (
            is_authorized or 
            path == protected_url or
            path.startswith('/static/') or 
            path.startswith('/media/') or
            path.startswith('/admin/') or
            path == '/favicon.ico'
        ):
            return self.get_response(request)

        return redirect(protected_url)