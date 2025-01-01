from django.urls import path
from .views import *

urlpatterns = [
    path("", index, name="index"),
    path("sites/", SitesListView.as_view(), name="sites-list"),
    path("sites/<int:pk>/", SitesDetailView.as_view(), name="sites-detail"),
    path("sites/create/", SitesCreateView.as_view(), name="sites-create"),
    path("sites/<int:pk>/update/", SitesUpdateView.as_view(), name="sites-update"),
    path("sites/<int:pk>/delete/", SitesDeleteView.as_view(), name="sites-delete"),
    path("<str:name>/<path:url>/", SitesConnectView.as_view(), name="sites-connect"),
]

app_name = "vpn-manager"
