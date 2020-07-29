from django.urls import path

from .views import *

urlpatterns = [
    path('my/posts/', PostOwner.as_view(), name="postowner"),
]
