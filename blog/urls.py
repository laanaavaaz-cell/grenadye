from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),

    # Explore & categories
    path('explore/', views.explore_view, name='explore'),
    path('explore/category/<slug:slug>/', views.category_view, name='category_view'),

    # Posts
    path('post/<int:pk>/', views.post_detail_view, name='post_detail'),
    path('post/<int:pk>/edit/', views.edit_post_view, name='edit_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/like/', views.like_comment, name='like_comment'),

    # Profile
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('settings/profile/', views.edit_profile_view, name='edit_profile'),
    path('user/<str:username>/follow/', views.follow_user, name='follow_user'),

    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('api/notifications/count/', views.notifications_count, name='notifications_count'),

    # Messaging
    path('messages/', views.inbox_view, name='inbox'),
    path('messages/group/<int:group_id>/', views.message_group_view, name='message_group'),
    path('messages/new-group/', views.create_group_view, name='create_group'),
    path('messages/dm/<str:username>/', views.start_dm_view, name='start_dm'),
]
