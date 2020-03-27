from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'


class ExportListView(TemplateView):
    template_name = 'export.html'
