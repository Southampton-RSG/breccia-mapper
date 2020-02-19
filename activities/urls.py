from django.urls import path

from . import views


app_name = 'activities'

urlpatterns = [
    path('activities',
         views.ActivityListView.as_view(),
         name='activity.list'),

    path('activities/<int:pk>',
         views.ActivityDetailView.as_view(),
         name='activity.detail'),
]
