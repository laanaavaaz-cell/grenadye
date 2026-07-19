import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Category, Post, Comment, Like, Notification, Profile, MessageGroup, Message
from .forms import RegisterForm, PostForm, PostEditForm, CommentForm, ProfileEditForm, MessageGroupForm, MessageForm


def _common_context(request):
    return {
        'categories': Category.objects.all(),
        'suggested_users': (
            User.objects.exclude(id=request.user.id)
                        .exclude(profile__followers=request.user.profile)[:5]
            if request.user.is_authenticated else User.objects.none()
        ),
    }


# ── AUTH ──────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    error = None
    if request.method == 'POST':
        identifier = request.POST.get('identifier', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=identifier, password=password)
        if not user:
            try:
                u = User.objects.get(email__iexact=identifier)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass
        if user:
            login(request, user)
            return redirect(request.GET.get('next', '/'))
        else:
            error = 'Invalid email/username or password.'
    return render(request, 'auth/login.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── HOME ──────────────────────────────────────────────────────

@login_required
def home_view(request):
    ctx = _common_context(request)
    profile = request.user.profile

    if request.method == 'POST':
        if not profile.can_post():
            return HttpResponseForbidden("You don't have permission to post.")
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('home')
    else:
        form = PostForm()

    category_slug = request.GET.get('category', '').strip()
    active_category = None
    if category_slug:
        try:
            active_category = Category.objects.get(slug=category_slug)
            posts = Post.objects.filter(category=active_category).select_related('user', 'user__profile', 'category')
        except Category.DoesNotExist:
            following_users = profile.following.values_list('user', flat=True)
            feed_ids = [request.user.id] + list(following_users)
            posts = Post.objects.filter(user_id__in=feed_ids).select_related('user', 'user__profile', 'category').distinct()
    else:
        following_users = profile.following.values_list('user', flat=True)
        feed_ids = [request.user.id] + list(following_users)
        posts = Post.objects.filter(user_id__in=feed_ids).select_related('user', 'user__profile', 'category').distinct()

    ctx.update({'posts': posts, 'form': form, 'active_category': active_category})
    return render(request, 'blog/home.html', ctx)


# ── EXPLORE ───────────────────────────────────────────────────

@login_required
def explore_view(request):
    ctx = _common_context(request)
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '').strip()

    posts = Post.objects.select_related('user', 'user__profile', 'category').all()
    users = User.objects.exclude(id=request.user.id).select_related('profile')

    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )

    active_category = None
    if category_slug:
        try:
            active_category = Category.objects.get(slug=category_slug)
            posts = posts.filter(category=active_category)
        except Category.DoesNotExist:
            pass

    if not query and not category_slug:
        posts = posts.order_by('-created_at')

    ctx.update({
        'posts': posts[:40],
        'users': users[:10],
        'active_category': active_category,
        'query': query,
    })
    return render(request, 'blog/explore.html', ctx)


@login_required
def category_view(request, slug):
    ctx = _common_context(request)
    category = get_object_or_404(Category, slug=slug)
    posts = Post.objects.filter(category=category).select_related('user', 'user__profile', 'category')
    ctx.update({'category': category, 'posts': posts})
    return render(request, 'blog/category.html', ctx)


# ── POST DETAIL ───────────────────────────────────────────────

@login_required
def post_detail_view(request, pk):
    ctx = _common_context(request)
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.filter(parent=None).select_related('user', 'user__profile').prefetch_related('replies__user', 'replies__user__profile')
    form = CommentForm()
    ctx.update({'post': post, 'comments': comments, 'form': form})
    return render(request, 'blog/post_detail.html', ctx)


@login_required
def edit_post_view(request, pk):
    ctx = _common_context(request)
    post = get_object_or_404(Post, pk=pk)

    # Only the post author (with can_post permission) can edit
    if post.user != request.user or not request.user.profile.can_post():
        return HttpResponseForbidden("You don't have permission to edit this post.")

    if request.method == 'POST':
        form = PostEditForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostEditForm(instance=post)

    ctx.update({'form': form, 'post': post})
    return render(request, 'blog/edit_post.html', ctx)


# ── PROFILE ───────────────────────────────────────────────────

@login_required
def profile_view(request, username):
    ctx = _common_context(request)
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    posts = Post.objects.filter(user=profile_user).select_related('user', 'user__profile', 'category')
    liked_post_ids = Like.objects.filter(user=profile_user, target_type='post').values_list('post_id', flat=True)
    liked_posts = Post.objects.filter(id__in=liked_post_ids).select_related('user', 'user__profile', 'category')
    ctx.update({
        'profile_user': profile_user,
        'profile': profile,
        'posts': posts,
        'liked_posts': liked_posts,
    })
    return render(request, 'blog/profile.html', ctx)


@login_required
def edit_profile_view(request):
    ctx = _common_context(request)
    profile = request.user.profile
    profile.refresh_from_db()
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            saved_profile = form.save()
            saved_profile.refresh_from_db()
            return redirect('profile', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile)
    ctx.update({'form': form, 'profile_obj': profile})
    return render(request, 'blog/edit_profile.html', ctx)


# ── NOTIFICATIONS ─────────────────────────────────────────────

@login_required
def notifications_view(request):
    ctx = _common_context(request)
    notifications = request.user.notifications.select_related('sender', 'sender__profile', 'post', 'comment').all()
    notifications.update(is_read=True)
    ctx.update({'notifications': notifications})
    return render(request, 'blog/notifications.html', ctx)


# ── MESSAGING ─────────────────────────────────────────────────

def _require_message_permission(user):
    return user.profile.can_message()


@login_required
def inbox_view(request):
    if not _require_message_permission(request.user):
        return HttpResponseForbidden("You need manager, staff, or admin status to access messages.")
    ctx = _common_context(request)
    groups = request.user.message_groups.prefetch_related('members', 'messages').order_by('-created_at')
    ctx.update({'groups': groups})
    return render(request, 'blog/inbox.html', ctx)


@login_required
def message_group_view(request, group_id):
    if not _require_message_permission(request.user):
        return HttpResponseForbidden("You need manager, staff, or admin status to access messages.")
    group = get_object_or_404(MessageGroup, pk=group_id)
    if request.user not in group.members.all():
        return HttpResponseForbidden("You are not a member of this group.")

    ctx = _common_context(request)
    # Mark messages as read
    group.messages.exclude(sender=request.user).update(is_read=True)

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.group = group
            msg.sender = request.user
            msg.save()
            # Notify other members
            for member in group.members.exclude(id=request.user.id):
                Notification.objects.create(
                    recipient=member,
                    sender=request.user,
                    notif_type='message',
                )
            return redirect('message_group', group_id=group.pk)
    else:
        form = MessageForm()

    messages_qs = group.messages.select_related('sender', 'sender__profile')
    ctx.update({'group': group, 'messages': messages_qs, 'form': form})
    return render(request, 'blog/message_group.html', ctx)


@login_required
def create_group_view(request):
    """Create a new named group chat — staff/superuser only."""
    if not request.user.profile.can_create_group():
        return HttpResponseForbidden("Only staff or admins can create group chats.")
    ctx = _common_context(request)
    if request.method == 'POST':
        form = MessageGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.created_by = request.user
            group.is_direct = False
            group.save()
            group.members.add(request.user)
            # Add selected members
            for member in form.cleaned_data.get('members', []):
                group.members.add(member)
            return redirect('message_group', group_id=group.pk)
    else:
        form = MessageGroupForm()
    ctx.update({'form': form})
    return render(request, 'blog/create_group.html', ctx)


@login_required
def start_dm_view(request, username):
    """Start or open a 1-to-1 DM thread with another user."""
    if not _require_message_permission(request.user):
        return HttpResponseForbidden("You need manager, staff, or admin status to send messages.")
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return redirect('inbox')

    # Look for existing DM between these two users
    existing = MessageGroup.objects.filter(
        is_direct=True,
        members=request.user
    ).filter(members=target)
    if existing.exists():
        return redirect('message_group', group_id=existing.first().pk)

    # Create new DM group
    group = MessageGroup.objects.create(
        created_by=request.user,
        is_direct=True,
    )
    group.members.add(request.user, target)
    return redirect('message_group', group_id=group.pk)


# ── AJAX ──────────────────────────────────────────────────────

@login_required
@require_POST
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    qs = Like.objects.filter(user=request.user, post=post, target_type='post')
    if qs.exists():
        qs.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, post=post, target_type='post')
        liked = True
        if post.user != request.user:
            Notification.objects.get_or_create(
                recipient=post.user, sender=request.user,
                notif_type='like', post=post,
                defaults={'is_read': False}
            )
    return JsonResponse({'liked': liked, 'likes_count': post.likes_count()})


@login_required
@require_POST
def like_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    qs = Like.objects.filter(user=request.user, comment=comment, target_type='comment')
    if qs.exists():
        qs.delete()
        liked = False
    else:
        Like.objects.create(user=request.user, comment=comment, target_type='comment')
        liked = True
        if comment.user != request.user:
            Notification.objects.create(
                recipient=comment.user, sender=request.user,
                notif_type='like', post=comment.post, comment=comment
            )
    return JsonResponse({'liked': liked, 'likes_count': comment.likes_count()})


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()
    if not content:
        return redirect('post_detail', pk=pk)

    parent_id = request.POST.get('parent_id', '').strip()
    parent = None
    if parent_id:
        try:
            parent = Comment.objects.get(pk=parent_id)
        except Comment.DoesNotExist:
            pass

    comment = Comment.objects.create(
        post=post, user=request.user, content=content, parent=parent
    )

    if parent:
        if parent.user != request.user:
            Notification.objects.create(
                recipient=parent.user, sender=request.user,
                notif_type='reply', post=post, comment=comment
            )
    elif post.user != request.user:
        Notification.objects.create(
            recipient=post.user, sender=request.user,
            notif_type='comment', post=post, comment=comment
        )

    return redirect('post_detail', pk=pk)


@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    profile = request.user.profile
    # Owner with can_post, staff, or superuser can delete
    if post.user != request.user and not (request.user.is_staff or request.user.is_superuser):
        return JsonResponse({'deleted': False, 'error': 'Forbidden'}, status=403)
    if post.user == request.user and not profile.can_post():
        return JsonResponse({'deleted': False, 'error': 'Forbidden'}, status=403)
    post.delete()
    return JsonResponse({'deleted': True})


@login_required
@require_POST
def follow_user(request, username):
    target_user = get_object_or_404(User, username=username)
    my_profile = request.user.profile
    target_profile = target_user.profile
    if target_profile in my_profile.following.all():
        my_profile.following.remove(target_profile)
        following = False
    else:
        my_profile.following.add(target_profile)
        following = True
        Notification.objects.create(
            recipient=target_user, sender=request.user, notif_type='follow'
        )
    return JsonResponse({'following': following, 'followers_count': target_profile.followers_count()})


@login_required
def notifications_count(request):
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'count': count})
