"""
Serialize models to and deserialize from JSON.
"""

from collections import OrderedDict
import typing

from rest_framework import serializers


class FlattenedModelSerializer(serializers.ModelSerializer):
    @classmethod
    def flatten_data(cls, data,
                     sub_type: typing.Type = dict,
                     sub_value_accessor: typing.Callable = lambda x: x.items()) -> OrderedDict:
        """
        Flatten a dictionary so that subdictionaries become a series of `key[.subkey[.subsubkey ...]]` entries
        in the top level dictionary.

        Works for other data structures (e.g. DRF Serializers) by providing suitable values for the
        `sub_type` and `sub_value_accessor` parameters.

        :param data: Dictionary or other data structure to flatten
        :param sub_type: Type to recursively flatten
        :param sub_value_accessor: Function to access keys and values contained within sub_type.
        """
        data_out = OrderedDict()

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

            elif value is not None:
                data_out[key] = value

        return data_out

    @property
    def column_headers(self) -> typing.List[str]:
        """
        Get all column headers that will be output by this serializer.
        """
        fields = self.flatten_data(self.fields,
                                   sub_type=serializers.BaseSerializer,
                                   sub_value_accessor=lambda x: x.fields.items())

        return list(fields)

    def to_representation(self, instance) -> OrderedDict:
        """

        """
        rep = super().to_representation(instance)

        rep = self.flatten_data(rep)

        return rep
