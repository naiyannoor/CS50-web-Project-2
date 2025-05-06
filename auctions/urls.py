from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category/<str:category_name>", views.category, name="category"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("create", views.create, name="create"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("edit/<int:listing_id>", views.edit, name="edit"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("mylistings", views.myListings, name="myListings")
]
