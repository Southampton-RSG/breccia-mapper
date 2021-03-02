from django.urls import path

from . import views


app_name = 'people'

urlpatterns = [
    ####################
    # Organisation views
    path('organisations/create',
         views.organisation.OrganisationCreateView.as_view(),
         name='organisation.create'),

    path('organisations',
         views.organisation.OrganisationListView.as_view(),
         name='organisation.list'),

    path('organisations/<int:pk>',
         views.organisation.OrganisationDetailView.as_view(),
         name='organisation.detail'),

    path('organisations/<int:pk>/update',
         views.organisation.OrganisationUpdateView.as_view(),
         name='organisation.update'),

    ##############
    # Person views
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

    ####################
    # Relationship views
    path('people/<int:person_pk>/relationships/create',
         views.relationship.RelationshipCreateView.as_view(),
         name='person.relationship.create'),

    path('relationships/<int:pk>',
         views.relationship.RelationshipDetailView.as_view(),
         name='relationship.detail'),

    path('relationships/<int:relationship_pk>/update',
         views.relationship.RelationshipUpdateView.as_view(),
         name='relationship.update'),

    ################################
    # OrganisationRelationship views
    path('organisations/<int:organisation_pk>/relationships/create',
         views.relationship.OrganisationRelationshipCreateView.as_view(),
         name='organisation.relationship.create'),

    path('organisation-relationships/<int:pk>',
         views.relationship.OrganisationRelationshipDetailView.as_view(),
         name='organisation.relationship.detail'),

    path('organisation-relationships/<int:relationship_pk>/update',
         views.relationship.OrganisationRelationshipUpdateView.as_view(),
         name='organisation.relationship.update'),

    ############
    # Data views
    path('map',
         views.person.PersonMapView.as_view(),
         name='person.map'),

    path('network',
         views.network.NetworkView.as_view(),
         name='network'),
]
