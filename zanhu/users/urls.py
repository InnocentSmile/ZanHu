from django.urls import path

from zanhu.users import views

app_name = "users"
urlpatterns = [
    path("update/", view=views.UserUpdateView.as_view(), name="update"),
    path("<str:username>/", view=views.UserDetailView.as_view(), name="detail"),
]
