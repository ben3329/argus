from django import template
from django.utils.safestring import mark_safe
from monitoring.models import AccessType, AssetType

register = template.Library()


@register.filter
def sub(value, arg):
    return value - arg


@register.filter
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '')
    return value.as_widget(attrs={'class': f'{css_classes} {arg}'})


@register.filter
def attr(value, arg):
    attrs = arg.split(':')
    if len(attrs) != 2:
        raise ValueError(
            "Invalid attribute syntax. Usage: {{ form.field_name|attr:'attribute:value' }}")
    attribute, value = attrs
    return value if attribute == 'value' else value.lower() if attribute == 'class' else value.capitalize() if attribute == 'id' else value


@register.filter(name='add_class_if')
def add_class_if(field, css_class):
    if field.errors:
        css_class += ' is-invalid'
    return mark_safe(str(field.as_widget(attrs={'class': css_class})))


@register.filter
def display_access_type(value):
    for choice in AccessType.choices:
        if choice[0] == value:
            return choice[1]
    return ''

@register.filter
def display_asset_type(value):
    for choice in AssetType.choices:
        if choice[0] == value:
            return choice[1]
    return ''
