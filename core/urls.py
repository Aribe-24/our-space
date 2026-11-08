from django.urls import path
from django.shortcuts import redirect
from . import views

urlpatterns = [
    path('', lambda r: redirect('dashboard'), name='root'),
    
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Core Actions
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('checkin/submit/', views.checkin_submit, name='checkin_submit'),
    path('tap-heart/', views.tap_heart, name='tap_heart'),
    path('dismiss-tap/<int:tap_id>/', views.dismiss_tap, name='dismiss_tap'),
    path('settings/update/', views.update_couple_settings, name='update_couple_settings'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Question of the Day
    path('questions/', views.questions_view, name='questions'),
    path('questions/<int:question_id>/answer/', views.submit_answer, name='submit_answer'),

    # Photo of the Day
    path('photos/', views.photos_view, name='photos'),
    path('photos/upload/', views.upload_photo, name='upload_photo'),
    path('photos/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),

    # Love Notes
    path('notes/', views.notes_view, name='notes'),
    path('notes/add/', views.add_love_note, name='add_love_note'),
    path('notes/<int:note_id>/pin/', views.toggle_pin_note, name='toggle_pin_note'),
    path('notes/<int:note_id>/delete/', views.delete_love_note, name='delete_love_note'),

    # Fun Extras
    path('extras/', views.extras_view, name='extras'),
    path('extras/this-or-that/<int:question_id>/vote/', views.vote_this_or_that, name='vote_this_or_that'),
    path('extras/songs/add/', views.add_song, name='add_song'),
    path('extras/milestones/add/', views.add_milestone, name='add_milestone'),
]
