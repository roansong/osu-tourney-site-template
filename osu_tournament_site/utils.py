import django
from django.template import TemplateDoesNotExist


def template_exists(template_name):
    try:
        django.template.loader.get_template(template_name=template_name)
    except TemplateDoesNotExist:
        return False
    return True
