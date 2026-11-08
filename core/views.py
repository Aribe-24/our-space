from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST

from .models import (
    UserProfile, CoupleSettings, DailyCheckIn, ThinkingOfYou,
    DailyQuestion, DailyAnswer, DailyPhoto, LoveNote,
    Song, Milestone, ThisOrThat, ThisOrThatVote
)
from .forms import (
    DailyCheckInForm, CoupleSettingsForm, UserProfileForm, MOOD_CHOICES,
    DailyAnswerForm, DailyPhotoForm, LoveNoteForm, SongForm, MilestoneForm
)


# ==============================================================================
# AUTHENTICATION
# ==============================================================================

def login_view(request):
    """Private login page for Jojo and Jay."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome home, {user.first_name or user.username}! 💕")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Incorrect username or password. This space is private to Jojo & Jay.")
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    """Log out and return to login screen."""
    logout(request)
    messages.info(request, "Logged out. See you soon, love! 💌")
    return redirect('login')


# ==============================================================================
# DASHBOARD ("OUR DAY")
# ==============================================================================

@login_required
def dashboard_view(request):
    """Our Day Dashboard: Clocks, Countdown, Check-in, Heart Tap."""
    today = timezone.localdate()
    couple_settings = CoupleSettings.load()

    # Current user & partner profiles
    my_profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'display_name': request.user.first_name or request.user.username.title()}
    )
    partner_user = User.objects.exclude(id=request.user.id).first()
    partner_profile = None
    if partner_user:
        partner_profile, _ = UserProfile.objects.get_or_create(
            user=partner_user,
            defaults={'display_name': partner_user.first_name or partner_user.username.title()}
        )

    # Check-ins
    my_checkin = DailyCheckIn.objects.filter(user=request.user, date=today).first()
    partner_checkin = None
    if partner_user:
        partner_checkin = DailyCheckIn.objects.filter(user=partner_user).order_by('-date', '-created_at').first()

    # Heart tap info
    recent_sent_tap = None
    if partner_user:
        recent_sent_tap = ThinkingOfYou.objects.filter(
            sender=request.user,
            receiver=partner_user
        ).order_by('-created_at').first()

    # Question of the day status preview
    total_q = DailyQuestion.objects.count() or 1
    day_idx = (couple_settings.days_together() % total_q) + 1
    today_question = DailyQuestion.objects.filter(day_number=day_idx).first() or DailyQuestion.objects.first()
    
    my_today_answer = None
    partner_today_answer = None
    if today_question:
        my_today_answer = DailyAnswer.objects.filter(question=today_question, user=request.user).first()
        if partner_user:
            partner_today_answer = DailyAnswer.objects.filter(question=today_question, user=partner_user).first()

    # Latest photos preview
    latest_photos = DailyPhoto.objects.all()[:3]

    # Latest pinned love notes
    pinned_notes = LoveNote.objects.filter(is_pinned=True)[:3]

    context = {
        'my_profile': my_profile,
        'partner_user': partner_user,
        'partner_profile': partner_profile,
        'couple_settings': couple_settings,
        'my_checkin': my_checkin,
        'partner_checkin': partner_checkin,
        'checkin_form': DailyCheckInForm(instance=my_checkin) if my_checkin else DailyCheckInForm(),
        'mood_choices': MOOD_CHOICES,
        'recent_sent_tap': recent_sent_tap,
        'today': today,
        'today_question': today_question,
        'my_today_answer': my_today_answer,
        'partner_today_answer': partner_today_answer,
        'latest_photos': latest_photos,
        'pinned_notes': pinned_notes,
        'settings_form': CoupleSettingsForm(instance=couple_settings),
        'profile_form': UserProfileForm(instance=my_profile),
    }
    return render(request, 'core/dashboard.html', context)


@login_required
@require_POST
def checkin_submit(request):
    """Creates or updates today's check-in."""
    today = timezone.localdate()
    existing = DailyCheckIn.objects.filter(user=request.user, date=today).first()
    form = DailyCheckInForm(request.POST, instance=existing)

    if form.is_valid():
        checkin = form.save(commit=False)
        checkin.user = request.user
        checkin.date = today
        checkin.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'mood_emoji': checkin.mood_emoji,
                'note': checkin.note,
                'message': 'Check-in saved! 🥰'
            })
        messages.success(request, f"Check-in saved! {checkin.mood_emoji} Shared with your love.")
    else:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Please enter a note'}, status=400)
        messages.error(request, "Please enter a short note for your check-in.")

    return redirect('dashboard')


@login_required
@require_POST
def tap_heart(request):
    """Sends a 'Thinking of You' tap to partner."""
    partner = User.objects.exclude(id=request.user.id).first()
    if not partner:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Partner not found'}, status=400)
        messages.error(request, "Partner account not found.")
        return redirect('dashboard')

    ThinkingOfYou.objects.create(sender=request.user, receiver=partner)
    time_str = timezone.now().strftime("%I:%M %p").lstrip("0")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"Sent a heart to {partner.first_name or partner.username}! 💕",
            'time': time_str,
        })

    messages.success(request, f"Sent a heart to {partner.first_name or partner.username}! 💕")
    return redirect('dashboard')


@login_required
@require_POST
def dismiss_tap(request, tap_id):
    """Dismisses heart tap notification."""
    tap = get_object_or_404(ThinkingOfYou, id=tap_id, receiver=request.user)
    tap.viewed = True
    tap.save()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))


@login_required
@require_POST
def update_couple_settings(request):
    """Updates anniversary date and countdown."""
    couple_settings = CoupleSettings.load()
    form = CoupleSettingsForm(request.POST, instance=couple_settings)
    if form.is_valid():
        form.save()
        messages.success(request, "Settings updated successfully! ✨")
    else:
        messages.error(request, "Error saving settings. Please check your dates.")
    return redirect('dashboard')


@login_required
@require_POST
def update_profile(request):
    """Updates user city, timezone, and hours."""
    profile = request.user.profile
    form = UserProfileForm(request.POST, instance=profile)
    if form.is_valid():
        form.save()
        messages.success(request, "Your profile and timezone have been updated! 🌸")
    else:
        messages.error(request, "Error updating profile. Please check the values.")
    return redirect('dashboard')


# ==============================================================================
# QUESTION OF THE DAY (DOUBLE-BLIND REVEAL)
# ==============================================================================

@login_required
def questions_view(request):
    """
    Daily Question with Double-Blind Reveal.
    Partner answers are only revealed once BOTH have answered!
    """
    couple_settings = CoupleSettings.load()
    partner_user = User.objects.exclude(id=request.user.id).first()

    # Determine today's question
    total_q = DailyQuestion.objects.count() or 1
    day_idx = (couple_settings.days_together() % total_q) + 1
    today_question = DailyQuestion.objects.filter(day_number=day_idx).first() or DailyQuestion.objects.first()

    my_answer = None
    partner_answer = None
    both_answered = False

    if today_question:
        my_answer = DailyAnswer.objects.filter(question=today_question, user=request.user).first()
        if partner_user:
            partner_answer = DailyAnswer.objects.filter(question=today_question, user=partner_user).first()
        both_answered = bool(my_answer and partner_answer)

    # Past answered questions
    answered_questions_ids = DailyAnswer.objects.filter(user=request.user).values_list('question_id', flat=True)
    past_questions = DailyQuestion.objects.filter(id__in=answered_questions_ids).exclude(id=today_question.id if today_question else 0)

    past_list = []
    for q in past_questions:
        q_my_ans = DailyAnswer.objects.filter(question=q, user=request.user).first()
        q_partner_ans = DailyAnswer.objects.filter(question=q, user=partner_user).first() if partner_user else None
        past_list.append({
            'question': q,
            'my_answer': q_my_ans,
            'partner_answer': q_partner_ans,
            'both_answered': bool(q_my_ans and q_partner_ans),
        })

    context = {
        'today_question': today_question,
        'my_answer': my_answer,
        'partner_answer': partner_answer,
        'both_answered': both_answered,
        'answer_form': DailyAnswerForm(instance=my_answer) if my_answer else DailyAnswerForm(),
        'past_list': past_list,
        'partner_user': partner_user,
    }
    return render(request, 'core/questions.html', context)


@login_required
@require_POST
def submit_answer(request, question_id):
    """Submits or updates answer for a question."""
    question = get_object_or_404(DailyQuestion, id=question_id)
    existing = DailyAnswer.objects.filter(question=question, user=request.user).first()
    form = DailyAnswerForm(request.POST, instance=existing)

    if form.is_valid():
        ans = form.save(commit=False)
        ans.question = question
        ans.user = request.user
        ans.save()
        messages.success(request, "Answer sealed! 💌 If your partner has answered, both are now revealed!")
    else:
        messages.error(request, "Please write an answer before submitting.")

    return redirect('questions')


# ==============================================================================
# PHOTO OF THE DAY (SHARED TIMELINE)
# ==============================================================================

@login_required
def photos_view(request):
    """Shared photo timeline and upload interface."""
    today = timezone.localdate()
    photos = DailyPhoto.objects.all()
    my_today_photo = DailyPhoto.objects.filter(user=request.user, date=today).first()

    context = {
        'photos': photos,
        'my_today_photo': my_today_photo,
        'photo_form': DailyPhotoForm(),
        'today': today,
    }
    return render(request, 'core/photos.html', context)


@login_required
@require_POST
def upload_photo(request):
    """Uploads today's photo."""
    form = DailyPhotoForm(request.POST, request.FILES)
    if form.is_valid():
        photo = form.save(commit=False)
        photo.user = request.user
        photo.date = timezone.localdate()
        photo.save()
        messages.success(request, "Photo posted to your shared timeline! 📸✨")
    else:
        messages.error(request, "Please choose an image file to upload.")

    return redirect('photos')


@login_required
@require_POST
def delete_photo(request, photo_id):
    """Deletes a photo."""
    photo = get_object_or_404(DailyPhoto, id=photo_id)
    if photo.user == request.user or request.user.is_superuser:
        photo.delete()
        messages.success(request, "Photo removed.")
    else:
        messages.error(request, "You can only delete your own photos.")
    return redirect('photos')


# ==============================================================================
# LOVE NOTES WALL
# ==============================================================================

@login_required
def notes_view(request):
    """Shared Love Notes Board."""
    notes = LoveNote.objects.all()
    form = LoveNoteForm()
    context = {
        'notes': notes,
        'form': form,
    }
    return render(request, 'core/notes.html', context)


@login_required
@require_POST
def add_love_note(request):
    """Adds a new love note to the board."""
    form = LoveNoteForm(request.POST)
    if form.is_valid():
        note = form.save(commit=False)
        note.author = request.user
        note.save()
        messages.success(request, "Love note pinned to the board! 💌")
    else:
        messages.error(request, "Please write something in your note.")
    return redirect('notes')


@login_required
@require_POST
def toggle_pin_note(request, note_id):
    """Pins or unpins a love note."""
    note = get_object_or_404(LoveNote, id=note_id)
    note.is_pinned = not note.is_pinned
    note.save()
    status = "pinned 📌" if note.is_pinned else "unpinned"
    messages.success(request, f"Note {status}.")
    return redirect('notes')


@login_required
@require_POST
def delete_love_note(request, note_id):
    """Deletes a love note."""
    note = get_object_or_404(LoveNote, id=note_id)
    note.delete()
    messages.success(request, "Note deleted.")
    return redirect('notes')


# ==============================================================================
# FUN EXTRAS (THIS OR THAT, PLAYLIST, MILESTONES)
# ==============================================================================

@login_required
def extras_view(request):
    """Fun extras: This or That game, shared playlist, memory milestones."""
    partner_user = User.objects.exclude(id=request.user.id).first()

    # This or That questions with voting states
    tot_questions = ThisOrThat.objects.all()
    tot_list = []
    for q in tot_questions:
        my_vote = ThisOrThatVote.objects.filter(question=q, user=request.user).first()
        partner_vote = ThisOrThatVote.objects.filter(question=q, user=partner_user).first() if partner_user else None
        is_match = bool(my_vote and partner_vote and my_vote.choice == partner_vote.choice)
        tot_list.append({
            'question': q,
            'my_vote': my_vote,
            'partner_vote': partner_vote,
            'is_match': is_match,
        })

    # Songs
    songs = Song.objects.all()

    # Milestones
    milestones = Milestone.objects.all()

    context = {
        'tot_list': tot_list,
        'songs': songs,
        'milestones': milestones,
        'song_form': SongForm(),
        'milestone_form': MilestoneForm(),
        'partner_user': partner_user,
    }
    return render(request, 'core/extras.html', context)


@login_required
@require_POST
def vote_this_or_that(request, question_id):
    """Votes on a This or That question."""
    question = get_object_or_404(ThisOrThat, id=question_id)
    choice = request.POST.get('choice')

    if choice in ['A', 'B']:
        vote, _ = ThisOrThatVote.objects.get_or_create(question=question, user=request.user)
        vote.choice = choice
        vote.save()

        partner = User.objects.exclude(id=request.user.id).first()
        partner_vote = ThisOrThatVote.objects.filter(question=question, user=partner).first() if partner else None
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'choice': choice,
                'partner_voted': bool(partner_vote),
                'partner_choice': partner_vote.choice if partner_vote else None,
                'is_match': bool(partner_vote and partner_vote.choice == choice),
            })
        messages.success(request, "Vote recorded! ✨")

    return redirect('extras')


@login_required
@require_POST
def add_song(request):
    """Adds a song to the shared playlist."""
    form = SongForm(request.POST)
    if form.is_valid():
        song = form.save(commit=False)
        song.added_by = request.user
        song.save()
        messages.success(request, f"Added '{song.title}' to our shared playlist! 🎵")
    else:
        messages.error(request, "Please provide the song title and artist.")
    return redirect('extras')


@login_required
@require_POST
def add_milestone(request):
    """Adds a milestone to the memories timeline."""
    form = MilestoneForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "Milestone added to our story! 🌟")
    else:
        messages.error(request, "Please check your milestone date and title.")
    return redirect('extras')
