from django import template
from django.contrib.auth.models import Group
register = template.Library()

# this is a custom tag to check if the user is a staff member or not

@register.filter(name='has_group')
def has_group(user, group_name):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()
