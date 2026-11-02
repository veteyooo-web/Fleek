"""Ограничения доступа по ролям."""
from functools import wraps

from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required

from .models import User


def role_required(role):
    """Декоратор: пускать только пользователей с указанной ролью (и суперпользователей)."""

    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if user.is_superuser or user.role == role:
                return view_func(request, *args, **kwargs)
            raise PermissionDenied(
                "Раздел доступен только для роли «%s»." % dict(User.Role.choices)[role]
            )

        return _wrapped

    return decorator


customer_required = role_required(User.Role.CUSTOMER)
freelancer_required = role_required(User.Role.FREELANCER)


class RoleRequiredMixin:
    """Mixin для классовых представлений: доступ только с указанной ролью."""

    required_role = None

    def dispatch(self, request, *args, **kwargs):
        user = getattr(request, "user", None)
        if (
            self.required_role
            and user
            and user.is_authenticated
            and not user.is_superuser
            and user.role != self.required_role
        ):
            raise PermissionDenied(
                "Раздел доступен только для роли «%s»."
                % dict(User.Role.choices)[self.required_role]
            )
        return super().dispatch(request, *args, **kwargs)


class CustomerRequiredMixin(RoleRequiredMixin):
    required_role = User.Role.CUSTOMER


class FreelancerRequiredMixin(RoleRequiredMixin):
    required_role = User.Role.FREELANCER
