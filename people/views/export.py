import csv
import typing

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic.list import BaseListView

from rest_framework.serializers import BaseSerializer

from .. import models, serializers


class CsvExportView(LoginRequiredMixin, BaseListView):
    model = None
    serializer_class = None

    @classmethod
    def flatten_data(cls, data,
                     sub_type: typing.Type = dict,
                     sub_value_accessor: typing.Callable = lambda x: x.items()) -> typing.Dict:
        """
        Flatten a dictionary so that subdictionaryies become a series of `key[.subkey[.subsubkey ...]]` entries
        in the top level dictionary.

        Works for other data structures (e.g. DRF Serializers) by providing suitable values for the
        `sub_type` and `sub_value_accessor` parameters.

        :param data: Dictionary or other data structure to flatten
        :param sub_type: Type to recursively flatten
        :param sub_value_accessor: Function to access keys and values contained within sub_type.
        """
        data_out = {}

        for key, value in sub_value_accessor(data):
            if isinstance(value, sub_type):
                # Recursively flatten nested structures of type `sub_type`
                sub_flattened = cls.flatten_data(value,
                                                 sub_type=sub_type,
                                                 sub_value_accessor=sub_value_accessor).items()

                # Enter recursively flattened values into result dictionary
                for sub_key, sub_value in sub_flattened:
                    # Keys in result dictionary are of format `key[.subkey[.subsubkey ...]]`
                    data_out[f'{key}.{sub_key}'] = sub_value
                    
            else:
                data_out[key] = value

        return data_out

    def render_to_response(self, context: typing.Dict) -> HttpResponse:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{self.get_context_object_name(self.object_list)}.csv"'
        
        serializer = self.serializer_class(self.get_queryset(), many=True)
        columns = self.flatten_data(serializer.child.fields,
                                    sub_type=BaseSerializer,
                                    sub_value_accessor=lambda x: x.fields.items())
        
        writer = csv.DictWriter(response, fieldnames=columns)
        writer.writeheader()
        
        for row in serializer.data:
            writer.writerow(self.flatten_data(row))
            
        return response


class PersonExportView(CsvExportView):
    model = models.Person
    serializer_class = serializers.PersonExportSerializer
    

class RelationshipExportView(CsvExportView):
    model = models.Relationship
    serializer_class = serializers.RelationshipSerializer
