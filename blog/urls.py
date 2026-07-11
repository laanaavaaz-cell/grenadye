from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('explore/', views.explore_view, name='explore'),
    path('explore/category/<slug:slug>/', views.category_view, name='category_view'),
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('settings/profile/', views.edit_profile_view, name='edit_profile'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),
    path('api/notifications/count/', views.notifications_count, name='notifications_count'),
]
