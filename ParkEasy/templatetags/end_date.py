from django import template
from django.contrib.auth.models import Group
register = template.Library()


@register.filter(name='end_date')
def end_date(length, start_date):
    group = Group.objects.get(name=group_name)
    return group in user.groups.all()