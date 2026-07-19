from django.contrib import admin
from .models import Category, Profile, Post, Comment, Like, Notification, MessageGroup, Message


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_editor', 'is_manager', 'location', 'created_at']
    list_filter = ['is_editor', 'is_manager']
    list_editable = ['is_editor', 'is_manager']
    search_fields = ['user__username', 'user__email']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'category', 'created_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'post', 'parent', 'created_at']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'target_type', 'post', 'comment']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'sender', 'notif_type', 'is_read', 'created_at']


@admin.register(MessageGroup)
class MessageGroupAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'is_direct', 'created_by', 'created_at']
    list_filter = ['is_direct']
    filter_horizontal = ['members']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'group', 'is_read', 'created_at']
    list_filter = ['is_read']
