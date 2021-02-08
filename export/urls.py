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

    path('export/person-answer-sets',
         views.people.PersonAnswerSetExportView.as_view(),
         name='person-answer-set'),

    path('export/relationships',
         views.people.RelationshipExportView.as_view(),
         name='relationship'),

    path('export/relationship-answer-sets',
         views.people.RelationshipAnswerSetExportView.as_view(),
         name='relationship-answer-set'),

    path('export/activities',
         views.activities.ActivityExportView.as_view(),
         name='activity'),

    path('export/activity-attendance',
         views.activities.ActivityAttendanceExportView.as_view(),
         name='activity-attendance'),
]
