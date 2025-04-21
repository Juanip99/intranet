from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def staff_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')  # Redirige a la página de inicio de sesión si no está autenticado
        if not request.user.is_staff:
            raise PermissionDenied  # Lanza una excepción de permiso denegado si no es staff
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

def group_required(group_names):
    def decorator(view_func):
        def _wrapped_view_func(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not request.user.groups.filter(name__in=group_names).exists() and not request.user.is_superuser:
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return _wrapped_view_func
    return decorator