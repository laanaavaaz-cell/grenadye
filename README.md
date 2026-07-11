# Grenadye.net — Social Blog App

A Twitter-style social blog built with Django, HTML, CSS, and JavaScript.

## Features

- 🔐 **Authentication** — Register & login by email OR username
- 📝 **Posts** — Create posts with optional title, image, and category
- 📂 **6 Categories** — Technology 💻, Travel ✈️, Food 🍕, Lifestyle 🌿, Sports ⚽, Music 🎵
- ❤️ **Post Likes** — AJAX animated heart toggle
- 💬 **Comments** — Nested replies with comment likes
- 👥 **Follow system** — Follow/unfollow users
- 🔔 **Notifications** — Likes, comments, replies, follows
- 👤 **Profile pages** — Header image, avatar, bio, stats, posts & liked tabs
- ✏️ **Edit profile** — Upload avatar & header, edit bio/location/website
- 🔍 **Explore** — Search posts & people, filter by category
- 📱 **Mobile-first** — Bottom nav on mobile, sidebar on desktop, right panel on wide screens
- 🌑 **Dark theme** — Twitter/X dark interface (pure black, `#1d9bf0` blue)

## Stack

- **Backend**: Django 4.x + SQLite
- **Frontend**: Vanilla JS (AJAX), CSS custom properties
- **Icons**: Font Awesome 6
- **Fonts**: Inter (Google Fonts)

## Run

```bash
cd grenadye
python3 manage.py runserver 0.0.0.0:9000
```

## Demo Accounts

| Username | Password | Email |
|----------|----------|-------|
| grenadye | demo1234 | demo@grenadye.net |
| alice    | demo1234 | alice@grenadye.net |
| bob      | demo1234 | bob@grenadye.net |
| sarah    | demo1234 | sarah@grenadye.net |
| marco    | demo1234 | marco@grenadye.net |

## Project Structure

```
grenadye/
├── grenadye/          # Django project settings
├── blog/              # Main app
│   ├── models.py      # Category, Profile, Post, Comment, Like, Notification
│   ├── views.py       # All views + AJAX endpoints
│   ├── forms.py       # RegisterForm, PostForm, CommentForm, ProfileEditForm
│   ├── urls.py        # All URL patterns
│   ├── admin.py       # Django admin registrations
│   └── templatetags/  # Custom filters: is_liked_by, post_likes_count, etc.
├── templates/
│   ├── base.html          # Bare HTML shell
│   ├── app_base.html      # Full layout (sidebar + main + right panel + modal)
│   ├── auth/              # login.html, register.html
│   └── blog/              # home, post_card, post_detail, explore,
│                          # category, profile, edit_profile, notifications
├── static/
│   ├── css/grenadye.css   # Full Twitter-dark theme (1100+ lines)
│   └── js/grenadye.js     # AJAX, modals, polling, toasts
└── media/                 # Uploaded avatars, headers, post images
```
