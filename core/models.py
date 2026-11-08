from datetime import datetime, timezone as dt_timezone
import zoneinfo
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class UserProfile(models.Model):
    """
    Profile data for Jojo and Jay including their cities,
    timezones, and sleep schedules.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    display_name = models.CharField(max_length=50)
    city = models.CharField(max_length=100, default='Kampala')
    timezone = models.CharField(max_length=100, default='Africa/Kampala')
    avatar_emoji = models.CharField(max_length=16, default='🌸')
    wake_hour = models.IntegerField(default=7, help_text="Typical wake hour (0-23, e.g. 7 for 7 AM)")
    sleep_hour = models.IntegerField(default=23, help_text="Typical sleep hour (0-23, e.g. 23 for 11 PM)")

    def __str__(self):
        return f"{self.display_name} ({self.city})"

    def get_local_datetime(self):
        """Returns the current local datetime object for this user's timezone."""
        try:
            tz = zoneinfo.ZoneInfo(self.timezone)
        except Exception:
            tz = zoneinfo.ZoneInfo("UTC")
        return timezone.now().astimezone(tz)

    def get_time_display(self):
        """Formats the current time, e.g. '09:42 PM'."""
        return self.get_local_datetime().strftime("%I:%M %p").lstrip("0")

    def get_date_display(self):
        """Formats current date, e.g. 'Sunday, Nov 8'."""
        return self.get_local_datetime().strftime("%A, %b %-d")

    def is_probably_awake(self):
        """
        Determines whether the user is likely awake based on their local hour.
        Handles wrap-around when sleep_hour > wake_hour (standard e.g. 7 to 23).
        """
        hour = self.get_local_datetime().hour
        if self.wake_hour <= self.sleep_hour:
            return self.wake_hour <= hour < self.sleep_hour
        else:
            # Shift work or inverted schedule
            return hour >= self.wake_hour or hour < self.sleep_hour

    def status_message(self):
        """Friendly, warm status note."""
        local_time = self.get_local_datetime()
        hour = local_time.hour
        is_awake = self.is_probably_awake()

        if not is_awake:
            if 0 <= hour < 5:
                return f"{self.display_name} is fast asleep in the dead of night 🌙"
            elif 5 <= hour < self.wake_hour:
                return f"{self.display_name} is probably snoozing soundly 💤"
            else:
                return f"{self.display_name} is probably sleeping 😴"
        else:
            if self.wake_hour <= hour < 11:
                return f"{self.display_name} is up and easing into the morning ☕"
            elif 11 <= hour < 14:
                return f"{self.display_name} is probably having lunch or in the zone ☀️"
            elif 14 <= hour < 18:
                return f"{self.display_name} is powering through the afternoon ✨"
            elif 18 <= hour < 21:
                return f"{self.display_name} is winding down the evening 🌆"
            else:
                return f"{self.display_name} is enjoying the night, getting sleepy 🕯️"


class CoupleSettings(models.Model):
    """
    Shared couple information: Anniversary date, next visit date, and title.
    Only one instance exists in the database.
    """
    anniversary_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date Jojo and Jay became an official couple"
    )
    next_visit_date = models.DateField(
        null=True,
        blank=True,
        help_text="The date of the next reunion / visit"
    )
    next_visit_title = models.CharField(
        max_length=120,
        default="Next time we hug 💕",
        help_text="Short title for the countdown"
    )
    app_title = models.CharField(
        max_length=120,
        default="Jojo & Jay's Space"
    )

    class Meta:
        verbose_name_plural = "Couple Settings"

    def __str__(self):
        return "Couple Settings"

    @classmethod
    def load(cls):
        """Singleton accessor."""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def days_together(self):
        """Calculates total days since anniversary."""
        if not self.anniversary_date:
            return 0
        today = timezone.localdate()
        delta = today - self.anniversary_date
        return max(0, delta.days)

    def days_until_visit(self):
        """Calculates days until next visit."""
        if not self.next_visit_date:
            return None
        today = timezone.localdate()
        delta = self.next_visit_date - today
        return delta.days


class DailyCheckIn(models.Model):
    """
    Daily mood emoji and short 'Today I...' note for each partner.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='checkins')
    date = models.DateField(default=timezone.localdate)
    mood_emoji = models.CharField(max_length=16, default='🥰')
    note = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date', '-updated_at']

    def __str__(self):
        return f"{self.user.username} ({self.date}): {self.mood_emoji} - {self.note[:30]}"


class ThinkingOfYou(models.Model):
    """
    A gentle heart tap sent from one partner to the other.
    """
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_taps')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_taps')
    created_at = models.DateTimeField(auto_now_add=True)
    viewed = models.BooleanField(default=False)
    note = models.CharField(max_length=140, blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tap from {self.sender.username} at {self.created_at}"


class DailyQuestion(models.Model):
    """
    A fun, deep, or romantic question for Jojo & Jay to answer.
    """
    question_text = models.TextField()
    category = models.CharField(max_length=50, default='Heart to Heart')
    day_number = models.IntegerField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['day_number']

    def __str__(self):
        return f"Day {self.day_number}: {self.question_text[:50]}"


class DailyAnswer(models.Model):
    """
    Private answer submitted by one partner.
    Revealed only when BOTH partners have answered!
    """
    question = models.ForeignKey(DailyQuestion, on_delete=models.CASCADE, related_name='answers')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_answers')
    answer_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'user')
        ordering = ['created_at']

    def __str__(self):
        return f"Answer by {self.user.username} to #{self.question.day_number}"


class DailyPhoto(models.Model):
    """
    One photo a day shared with a caption in a shared timeline.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='photos/%Y/%m/')
    caption = models.CharField(max_length=280, blank=True)
    date = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"Photo by {self.user.username} on {self.date}"


class LoveNote(models.Model):
    """
    A sticky love note or inside joke on the shared wall.
    """
    COLOR_CHOICES = [
        ('pink', 'Blush Pink'),
        ('cream', 'Warm Cream'),
        ('lavender', 'Soft Lavender'),
        ('peach', 'Peach Blossom'),
        ('plum', 'Cozy Plum'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='love_notes')
    content = models.TextField()
    color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='pink')
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"Note by {self.author.username} ({self.created_at.strftime('%b %d')})"


class Song(models.Model):
    """
    A song in their shared playlist.
    """
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='songs')
    title = models.CharField(max_length=150)
    artist = models.CharField(max_length=150)
    url = models.URLField(blank=True, help_text="Link to Spotify, YouTube, Apple Music, etc.")
    note = models.CharField(max_length=280, blank=True, help_text="Why this reminds me of you...")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.artist}"


class Milestone(models.Model):
    """
    Special milestone in their journey together.
    """
    title = models.CharField(max_length=150)
    date = models.DateField()
    description = models.TextField(blank=True)
    emoji = models.CharField(max_length=16, default='🌟')

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.date}: {self.title}"


class ThisOrThat(models.Model):
    """A fun 'This or That' question for Jojo and Jay."""
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    emoji_a = models.CharField(max_length=16, default='☕')
    emoji_b = models.CharField(max_length=16, default='🍵')
    category = models.CharField(max_length=50, default='Lifestyle')

    def __str__(self):
        return f"{self.option_a} OR {self.option_b}"


class ThisOrThatVote(models.Model):
    """Vote submitted by one of the partners."""
    question = models.ForeignKey(ThisOrThat, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='this_or_that_votes')
    choice = models.CharField(max_length=1, choices=[('A', 'Option A'), ('B', 'Option B')])
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'user')

    def __str__(self):
        return f"{self.user.username} picked {self.choice} on #{self.question_id}"
