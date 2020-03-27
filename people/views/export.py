import csv
import typing

from django.http import HttpResponse
from django.views.generic.list import BaseListView

from .. import models, serializers


class CsvExportView(BaseListView):
    model = None
    serializer_class = None

    def render_to_response(self, context: typing.Dict) -> HttpResponse:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_context_object_name(self.object_list)}.csv"'
        
        serializer = self.serializer_class(self.get_queryset(), many=True)
        writer = csv.DictWriter(response, fieldnames=self.serializer_class.Meta.fields)
        writer.writeheader()
        writer.writerows(serializer.data)
            
        return response


class PersonExportView(CsvExportView):
    model = models.Person
    serializer_class = serializers.PersonExportSerializer
    

class RelationshipExportView(CsvExportView):
    model = models.Relationship
    serializer_class = serializers.RelationshipSerializer
