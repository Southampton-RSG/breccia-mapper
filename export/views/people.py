from . import base
from .. import serializers

from people import models


class PersonExportView(base.CsvExportView):
    model = models.person.Person
    serializer_class = serializers.people.PersonSerializer


class RelationshipExportView(base.CsvExportView):
    model = models.relationship.Relationship
    serializer_class = serializers.people.RelationshipSerializer


class RelationshipAnswerSetExportView(base.CsvExportView):
    model = models.relationship.RelationshipAnswerSet
    serializer_class = serializers.people.RelationshipAnswerSetSerializer
