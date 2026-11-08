from django import forms
from .models import (
    DailyCheckIn, CoupleSettings, UserProfile,
    DailyAnswer, DailyPhoto, LoveNote, Song, Milestone
)

MOOD_CHOICES = [
    ('🥰', 'Loved & Cozy'),
    ('✨', 'Happy & Inspired'),
    ('☕', 'Chill & Relaxed'),
    ('😴', 'Sleepy / Tired'),
    ('🥺', 'Missing You'),
    ('💪', 'Productive & Strong'),
    ('🥳', 'Excited & Joyful'),
    ('🌧️', 'A Bit Down / Low Energy'),
    ('🎉', 'Celebrating'),
    ('🤗', 'Need a Warm Hug'),
]

class DailyCheckInForm(forms.ModelForm):
    class Meta:
        model = DailyCheckIn
        fields = ['mood_emoji', 'note']
        widgets = {
            'mood_emoji': forms.HiddenInput(),
            'note': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Today I made coffee, went for a walk, missed your voice...',
                'maxlength': '280',
                'required': True,
                'autocomplete': 'off',
            }),
        }


class CoupleSettingsForm(forms.ModelForm):
    class Meta:
        model = CoupleSettings
        fields = ['anniversary_date', 'next_visit_date', 'next_visit_title', 'app_title']
        widgets = {
            'anniversary_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'next_visit_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'next_visit_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Next time we hug 💕'}),
            'app_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': "e.g. Jojo & Jay's Space"}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['display_name', 'city', 'timezone', 'avatar_emoji', 'wake_hour', 'sleep_hour']
        widgets = {
            'display_name': forms.TextInput(attrs={'class': 'form-input'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Kampala'}),
            'timezone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. Africa/Kampala'}),
            'avatar_emoji': forms.TextInput(attrs={'class': 'form-input', 'style': 'font-size: 1.25rem;'}),
            'wake_hour': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 23}),
            'sleep_hour': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'max': 23}),
        }


class DailyAnswerForm(forms.ModelForm):
    class Meta:
        model = DailyAnswer
        fields = ['answer_text']
        widgets = {
            'answer_text': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Write your honest answer here... It will stay secret until your partner answers too 💌',
                'required': True,
            }),
        }


class DailyPhotoForm(forms.ModelForm):
    class Meta:
        model = DailyPhoto
        fields = ['image', 'caption']
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-file-input',
                'accept': 'image/*',
                'id': 'photo-file-input',
                'required': True,
            }),
            'caption': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'A little memory from today...',
                'maxlength': '280',
            }),
        }


class LoveNoteForm(forms.ModelForm):
    class Meta:
        model = LoveNote
        fields = ['content', 'color', 'is_pinned']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'A sweet thought, an inside joke, or something you love about them...',
                'required': True,
            }),
            'color': forms.Select(attrs={'class': 'form-input'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'artist', 'url', 'note']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Song Title', 'required': True}),
            'artist': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Artist', 'required': True}),
            'url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'Spotify or YouTube link'}),
            'note': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Why this song reminds me of you...'}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'date', 'emoji', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Milestone Title', 'required': True}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input', 'required': True}),
            'emoji': forms.TextInput(attrs={'class': 'form-input', 'style': 'font-size: 1.25rem;'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'A few words about this moment...'}),
        }
