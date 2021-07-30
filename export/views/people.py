from . import base
from .. import serializers

from people import models


class PersonExportView(base.CsvExportView):
    model = models.person.Person
    serializer_class = serializers.people.PersonSerializer


class PersonAnswerSetExportView(base.CsvExportView):
    model = models.person.PersonAnswerSet
    serializer_class = serializers.people.PersonAnswerSetSerializer


class RelationshipExportView(base.CsvExportView):
    model = models.relationship.Relationship
    serializer_class = serializers.people.RelationshipSerializer


class RelationshipAnswerSetExportView(base.CsvExportView):
    model = models.relationship.RelationshipAnswerSet
    serializer_class = serializers.people.RelationshipAnswerSetSerializer


class OrganisationExportView(base.CsvExportView):
    model = models.person.Organisation
    serializer_class = serializers.people.OrganisationSerializer


class OrganisationAnswerSetExportView(base.CsvExportView):
    model = models.organisation.OrganisationAnswerSet
    serializer_class = serializers.people.OrganisationAnswerSetSerializer


class OrganisationRelationshipExportView(base.CsvExportView):
    model = models.relationship.OrganisationRelationship
    serializer_class = serializers.people.OrganisationRelationshipSerializer


class OrganisationRelationshipAnswerSetExportView(base.CsvExportView):
    model = models.relationship.OrganisationRelationshipAnswerSet
    serializer_class = serializers.people.OrganisationRelationshipAnswerSetSerializer
