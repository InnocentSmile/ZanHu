from django.urls import path

from zanhu.news import views

app_name = "news"
urlpatterns = [
    path("", view=views.NewsListView.as_view(), name="list"),
    path('post-news/', views.post_new, name="post_news"),
    path('delete/<str:pk>/', views.NewsDeleteView.as_view(), name="delete_news"),
    path('like/', views.like, name="like_post"),
    path('get-thread/', views.get_thread, name="get_thread"),
    path('post-comment/', views.post_comment, name="post_comments"),
    path('sub-nums/', views.sub_nums, name="sub_nums"),
    path('update-interactions/', views.update_interactions, name='update_interactions'),
]
