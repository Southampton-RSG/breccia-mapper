"""breccia_mapper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.conf.urls.static import static

from . import views

from constance import config

admin.site.site_header = config.PROJECT_LONG_NAME + " Admin"
admin.site.site_title = config.PROJECT_SHORT_NAME + " Admin"

urlpatterns = [
    path('admin/',
         admin.site.urls),

    path('select2/',
         include('django_select2.urls')),

    path('hijack/',
         include('hijack.urls', namespace='hijack')),

    path('',
         include('django.contrib.auth.urls')),

    path('',
         views.IndexView.as_view(),
         name='index'),

    path('consent',
         views.ConsentTextView.as_view(),
         name='consent'),

    path('',
         include('export.urls')),

    path('',
         include('people.urls')),

    path('',
         include('activities.urls')),
]  # yapf: disable
