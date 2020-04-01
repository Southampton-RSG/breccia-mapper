from django.urls import path

from . import views


app_name = 'export'

urlpatterns = [
    path('export',
         views.ExportListView.as_view(),
         name='index'),

    path('export/people',
         views.people.PersonExportView.as_view(),
         name='person'),

    path('export/relationships',
         views.people.RelationshipExportView.as_view(),
         name='relationship'),

    path('export/activities',
         views.activities.ActivityExportView.as_view(),
         name='activity'),
]
