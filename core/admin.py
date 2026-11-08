from django.contrib import admin
from .models import (
    UserProfile, CoupleSettings, DailyCheckIn, ThinkingOfYou,
    DailyQuestion, DailyAnswer, DailyPhoto, LoveNote, Song, Milestone
)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'city', 'timezone', 'avatar_emoji', 'wake_hour', 'sleep_hour')

@admin.register(CoupleSettings)
class CoupleSettingsAdmin(admin.ModelAdmin):
    list_display = ('app_title', 'anniversary_date', 'next_visit_date', 'next_visit_title')

@admin.register(DailyCheckIn)
class DailyCheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'mood_emoji', 'note', 'created_at')
    list_filter = ('user', 'date')

@admin.register(ThinkingOfYou)
class ThinkingOfYouAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'created_at', 'viewed')
    list_filter = ('viewed', 'sender')

@admin.register(DailyQuestion)
class DailyQuestionAdmin(admin.ModelAdmin):
    list_display = ('day_number', 'category', 'question_text', 'is_active')
    search_fields = ('question_text',)

@admin.register(DailyAnswer)
class DailyAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'created_at')
    list_filter = ('user', 'question')

@admin.register(DailyPhoto)
class DailyPhotoAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'caption', 'created_at')
    list_filter = ('user', 'date')

@admin.register(LoveNote)
class LoveNoteAdmin(admin.ModelAdmin):
    list_display = ('author', 'color', 'is_pinned', 'created_at')
    list_filter = ('is_pinned', 'color', 'author')

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'added_by', 'created_at')

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'emoji')
