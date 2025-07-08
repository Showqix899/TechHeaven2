from django.http import HttpResponseForbidden
from functools import wraps
#render
from django.shortcuts import render,redirect

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.role == "ADMIN":
            return view_func(request, *args, **kwargs)
        return render(request,'accounts/error_message.html',{'message':'You do not have permission to access this page.'})
    return _wrapped_view
