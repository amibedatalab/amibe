from django import template

register = template.Library()


@register.filter(name='user_has_permission')
def user_has_permission(user, permission_codename):
    return user.has_perm(permission_codename) or \
        user.groups.filter(permissions__codename=permission_codename).exists()
