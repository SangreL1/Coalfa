from django.shortcuts import redirect
from django.urls import reverse

class AdminAccessMiddleware:
    """
    Middleware to restrict access to the Django admin interface.
    Only allows access to authenticated users with is_staff=True.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for the admin panel
        if request.path.startswith('/admin/'):
            # Allow access only if the user is authenticated and is staff
            if not request.user.is_authenticated or not request.user.is_staff:
                # Redirect to the main login page
                return redirect('login')
        
        response = self.get_response(request)
        return response

class PreventCachingMiddleware:
    """
    Middleware to prevent the browser from caching sensitive pages.
    This ensures that the back button doesn't show old session data.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add headers to prevent caching for all responses
        # Or you could restrict this to only authenticated users if preferred:
        # if request.user.is_authenticated:
        if response:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = 'Sat, 01 Jan 2000 00:00:00 GMT'
        
        return response
