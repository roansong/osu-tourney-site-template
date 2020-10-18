from django.views.generic import TemplateView

from osu_tournament_site.utils import template_exists

INDEX_TEMPLATE_NAME = "index.html"
ABOUT_TEMPLATE_NAME = "about.html"


class IndexView(TemplateView):
    template_name = "default/index.html"

    def __init__(self):
        super().__init__()
        if template_exists(INDEX_TEMPLATE_NAME):
            self.template_name = INDEX_TEMPLATE_NAME


class AboutView(TemplateView):
    template_name = "default/about.html"

    def __init__(self):
        super().__init__()
        if template_exists(ABOUT_TEMPLATE_NAME):
            self.template_name = ABOUT_TEMPLATE_NAME
