from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Post, Comment, Profile


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
    """
    Wraps Profile fields + User.first_name / User.last_name in one form.
    Initial values for first_name / last_name are populated from the related
    User instance so the template can just render {{ form.first_name.value }}.
    On save, both User and Profile are persisted.
    """
    first_name = forms.CharField(max_length=30, required=False, label='First name')
    last_name  = forms.CharField(max_length=30, required=False, label='Last name')

    class Meta:
        model  = Profile
        fields = ['avatar', 'header_image', 'bio', 'location', 'website']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Seed User name fields from the related User object.
        # Works whether the form is unbound (GET) or re-bound after failed POST.
        if self.instance and self.instance.pk:
            user = self.instance.user
            # Only set initial when NOT submitted (unbound form).
            # For a bound form Django already has the POST data.
            if not self.is_bound:
                self.fields['first_name'].initial = user.first_name
                self.fields['last_name'].initial  = user.last_name

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name  = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            profile.save()
        return profile
