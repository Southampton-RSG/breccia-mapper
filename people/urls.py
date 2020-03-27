from django.urls import path

from . import views


app_name = 'people'

urlpatterns = [
    path('profile/',
         views.person.ProfileView.as_view(),
         name='person.profile'),

    path('people/create',
         views.person.PersonCreateView.as_view(),
         name='person.create'),

    path('people',
         views.person.PersonListView.as_view(),
         name='person.list'),

    path('people/<int:pk>',
         views.person.ProfileView.as_view(),
         name='person.detail'),

    path('people/<int:pk>/update',
         views.person.PersonUpdateView.as_view(),
         name='person.update'),

    path('people/<int:person_pk>/relationships/create',
         views.relationship.RelationshipCreateView.as_view(),
         name='person.relationship.create'),

    path('relationships/<int:pk>',
         views.relationship.RelationshipDetailView.as_view(),
         name='relationship.detail'),

    path('relationships/<int:relationship_pk>/update',
         views.relationship.RelationshipUpdateView.as_view(),
         name='relationship.update'),

    path('people/export',
         views.export.PersonExportView.as_view(),
         name='person.export'),

    path('relationships/export',
         views.export.RelationshipExportView.as_view(),
         name='relationship.export'),

    path('network',
         views.network.NetworkView.as_view(),
         name='network'),
]
