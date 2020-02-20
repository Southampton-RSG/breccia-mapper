from django.urls import path

from . import views


app_name = 'people'

urlpatterns = [
    path('profile/',
         views.ProfileView.as_view(),
         name='person.profile'),

    path('people/create',
         views.PersonCreateView.as_view(),
         name='person.create'),

    path('people',
         views.PersonListView.as_view(),
         name='person.list'),

    path('people/<int:pk>',
         views.ProfileView.as_view(),
         name='person.detail'),

    path('people/<int:person_pk>/relationships/create',
         views.RelationshipCreateView.as_view(),
         name='person.relationship.create'),

    path('relationships/<int:pk>',
         views.RelationshipDetailView.as_view(),
         name='relationship.detail'),
]
