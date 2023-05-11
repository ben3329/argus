from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions


class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if (request.method in permissions.SAFE_METHODS) or request.user.is_superuser:
            return True
        return obj.author == request.user


class HasAddPermissionWithPost(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            model = view.get_queryset().model
            content_type = ContentType.objects.get_for_model(model)
            permission = Permission.objects.filter(
                content_type=content_type,
                codename='add_{}'.format(model.__name__.lower()))
            return request.user.has_perm(permission)
        else:
            return True
