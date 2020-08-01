from django.urls import path

from .views import *

urlpatterns = [
    path('my/', Owner.as_view(), name="owner"),
    path('my/posts/', PostOwner.as_view(), name="postowner"),
    path('my/top/', TopOwner.as_view(), name="topowner"),
    path('my/urgent/', UrgentOwner.as_view(), name="urgentowner"),
    path('my/general/', GeneralOwner.as_view(), name="generalowner"),

    path('users/user/', OtherUser.as_view(), name="otheruser"),
    path('users/user/post/', OtherPost.as_view(), name="otherpost"),

    path('random/general/', GeneralRandom.as_view(), name="randomgeneral"),

    path('posts/search/', SimpleSearch.as_view(), name="simplesearch"),
    path('posts/category/', CategoryPosts.as_view(), name="postscategory"),
]
