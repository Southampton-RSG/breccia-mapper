from . import base
from .. import serializers

from activities import models


class ActivityExportView(base.CsvExportView):
    model = models.Activity
    serializer_class = serializers.activities.ActivitySerializer
