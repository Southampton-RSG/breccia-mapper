"""
Admin site panels for models in the People app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from . import models


admin.site.register(models.User, UserAdmin)


@admin.register(models.Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Role)
class RoleAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Theme)
class ThemeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Person)
class PersonAdmin(admin.ModelAdmin):
    pass


@admin.register(models.RelationshipQuestionChoice)
class RelationshipQuestionChoiceAdmin(admin.ModelAdmin):
    pass


class RelationshipQuestionChoiceInline(admin.TabularInline):
    model = models.RelationshipQuestionChoice


@admin.register(models.RelationshipQuestion)
class RelationshipQuestionAdmin(admin.ModelAdmin):
    inlines = [
        RelationshipQuestionChoiceInline,
    ]


@admin.register(models.Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    pass
