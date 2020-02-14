"""
Admin site panels for models in the Activities app.
"""

from django.contrib import admin

from . import models


@admin.register(models.ActivitySeries)
class ActivitySeriesAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Activity)
class ActivityAdmin(admin.ModelAdmin):
    pass
