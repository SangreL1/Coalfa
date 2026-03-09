from django import template

register = template.Library()


@register.filter
def get_item(obj, key):
    """Acceso a dict por clave variable."""
    try:
        return obj.get(key)
    except (AttributeError, KeyError, TypeError):
        return None


@register.filter
def replace(value, arg):
    """Reemplazo simple: 'old,new'."""
    if ',' not in arg:
        return value
    old, new = arg.split(',', 1)
    return value.replace(old, new)


@register.filter
def startswith(value, arg):
    """Verifica si un string empieza con arg."""
    return str(value).startswith(arg)


@register.filter
def intcomma(value):
    """Formatea un número con puntos como separadores de miles."""
    try:
        value = int(value)
        return "{:,}".format(value).replace(",", ".")
    except (ValueError, TypeError):
        return value
