from django import template
from blog.models import Like

register = template.Library()

@register.filter
def is_liked_by(obj, user):
    if not user.is_authenticated:
        return False
    if hasattr(obj, 'comments'):  # It's a Post
        return Like.objects.filter(user=user, post=obj, target_type='post').exists()
    else:  # It's a Comment
        return Like.objects.filter(user=user, comment=obj, target_type='comment').exists()

@register.filter
def post_likes_count(post):
    return Like.objects.filter(post=post, target_type='post').count()

@register.filter
def comment_likes_count(comment):
    return Like.objects.filter(comment=comment, target_type='comment').count()

@register.filter
def comments_count(post):
    return post.comments.count()

@register.filter
def is_following(profile, target_profile):
    return profile.following.filter(id=target_profile.id).exists()
