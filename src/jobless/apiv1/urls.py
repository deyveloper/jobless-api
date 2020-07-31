from django.urls import path

from .views import *

urlpatterns = [
    path('my/', Owner.as_view(), name="owner"),
    path('my/posts/', PostOwner.as_view(), name="postowner"),
    path('my/top/', TopOwner.as_view(), name="topowner"),
    path('my/urgent/', UrgentOwner.as_view(), name="urgentowner"),
    path('my/general/', GeneralOwner.as_view(), name="generalowner"),
]
