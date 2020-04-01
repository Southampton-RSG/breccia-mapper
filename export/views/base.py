import csv
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.list import BaseListView


class CsvExportView(LoginRequiredMixin, BaseListView):
    model = None
    serializer_class = None

    def render_to_response(self, context: typing.Dict) -> HttpResponse:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_context_object_name(self.object_list)}.csv"'

        # Force ordering by PK - though this should be default anyway
        serializer = self.serializer_class(self.get_queryset().order_by('pk'), many=True)

        writer = csv.DictWriter(response, fieldnames=serializer.child.column_headers)
        writer.writeheader()
        writer.writerows(serializer.data)
        
        return response


class ExportListView(LoginRequiredMixin, TemplateView):
    template_name = 'export/export.html'
