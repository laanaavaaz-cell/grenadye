from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Profile, MessageGroup, Message


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=60, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'full_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        full_name = self.cleaned_data.get('full_name', '')
        if full_name:
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
        if commit:
            user.save()
        return user


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': "What's on your mind?",
                'rows': 3,
            }),
            'title': forms.TextInput(attrs={'placeholder': 'Title (optional)'}),
        }


class PostEditForm(forms.ModelForm):
    """Form for editing an existing post (author + can_post users)."""
    class Meta:
        model = Post
        fields = ['title', 'content', 'image', 'category']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': "What's on your mind?",
                'rows': 5,
            }),
            'title': forms.TextInput(attrs={'placeholder': 'Title (optional)'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Post your reply',
                'rows': 2,
            })
        }


class ProfileEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=False, label='First name')
    last_name = forms.CharField(max_length=30, required=False, label='Last name')

    class Meta:
        model = Profile
        fields = ['avatar', 'header_image', 'bio', 'location', 'website']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            user = self.instance.user
            if not self.is_bound:
                self.fields['first_name'].initial = user.first_name
                self.fields['last_name'].initial = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            profile.save()
        return profile


class MessageGroupForm(forms.ModelForm):
    """Form for creating a new named group chat (staff/superuser only)."""
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Add members',
        help_text='Select users to add to this group.',
    )

    class Meta:
        model = MessageGroup
        fields = ['name', 'description', 'members']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Group name'}),
            'description': forms.TextInput(attrs={'placeholder': 'Short description (optional)'}),
        }


class MessageForm(forms.ModelForm):
    """Form for sending a message inside a group."""
    class Meta:
        model = Message
        fields = ['content', 'image']
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Type a message…',
                'rows': 2,
            }),
        }
