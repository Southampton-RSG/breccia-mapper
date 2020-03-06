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

    path('people/<int:pk>/update',
         views.PersonUpdateView.as_view(),
         name='person.update'),

    path('people/<int:person_pk>/relationships/create',
         views.RelationshipCreateView.as_view(),
         name='person.relationship.create'),

    path('relationships/<int:pk>',
         views.RelationshipDetailView.as_view(),
         name='relationship.detail'),

    path('relationships/<int:relationship_pk>/update',
         views.RelationshipUpdateView.as_view(),
         name='relationship.update'),

    path('api/people',
         views.PersonApiView.as_view(),
         name='person.api.list'),

    path('api/relationships',
         views.RelationshipApiView.as_view(),
         name='relationship.api.list'),

    path('network',
         views.NetworkView.as_view(),
         name='network'),
]
