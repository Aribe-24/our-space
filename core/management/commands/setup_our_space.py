from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import (
    UserProfile, CoupleSettings, DailyQuestion, DailyCheckIn, LoveNote,
    Song, Milestone, ThisOrThat, ThisOrThatVote
)

SEED_QUESTIONS = [
    # Romantic & Deep
    ("What was the exact moment you realized you had feelings for me?", "Romantic"),
    ("What is your favorite memory of us being together in person?", "Romantic"),
    ("What is one little thing I do that always makes you smile, even through a screen?", "Romantic"),
    ("If we could wake up anywhere in the world together tomorrow, where would we be?", "Dreams"),
    ("What song will forever remind you of us?", "Memories"),
    ("What is one habit of mine that you find unexpectedly endearing?", "Silly"),
    ("What does your ideal lazy Sunday with me look like from morning to night?", "Dreams"),
    ("When do you miss me the most during your normal day?", "Heart to Heart"),
    ("What is something you’ve learned about love since being with me?", "Heart to Heart"),
    ("What is our best inside joke, and how did it start?", "Memories"),
    ("What was your very first impression of me when we first met?", "Memories"),
    ("What is one place in your city you can't wait to show me?", "Connection"),
    ("If our relationship was a movie or a book, what would the title be?", "Playful"),
    ("What is something you appreciate about how we handle long distance?", "Heart to Heart"),
    ("What’s a small gift or gesture from me that meant the world to you?", "Memories"),
    ("What are three words you would use to describe our connection?", "Romantic"),
    ("What is your absolute favorite physical feature of mine?", "Flirty"),
    ("What outfit of mine is your favorite?", "Flirty"),
    ("What is a sweet dream you've had about us?", "Romantic"),
    ("What is one thing on your bucket list that we must do together?", "Dreams"),
    ("What meal should we cook together the next time we're in the same kitchen?", "Food & Fun"),
    ("If we could adopt any pet together, what would we get and what would we name it?", "Playful"),
    ("What is the funniest text or photo I have ever sent you?", "Playful"),
    ("What makes you feel most loved and cared for when we're apart?", "Heart to Heart"),
    ("If you could teleport to give me a 5-minute hug right now, would you?", "Romantic"),
    ("What scent or smell instantly reminds you of me?", "Memories"),
    ("What is something new you want us to learn or try together?", "Dreams"),
    ("What is your favorite photo of us together and why?", "Memories"),
    ("What is a quirk of mine that only you really know about?", "Silly"),
    ("What does home feel like to you?", "Deep"),
    ("What are you most proud of in our relationship?", "Heart to Heart"),
    ("If we were stranded on a deserted island together, who would be in charge of what?", "Playful"),
    ("What is your favorite comfort food when you're feeling down?", "Favorites"),
    ("What is the most thoughtful compliment you've ever received from me?", "Heart to Heart"),
    ("What is one thing we always disagree on playfully?", "Playful"),
    ("What is your favorite season of the year to spend together?", "Romantic"),
    ("What's a secret silly superpower you wish you had?", "Silly"),
    ("If we had a secret handshake, what would the grand finale move be?", "Playful"),
    ("What is something that made you laugh out loud today?", "Today"),
    ("What is the best part of your daily routine right now?", "Connection"),
    ("What is one goal you want to achieve this year, and how can I cheer you on?", "Support"),
    ("What is something you wish I was there to help you with today?", "Heart to Heart"),
    ("What is the best dessert in the world according to your tastebuds?", "Food & Fun"),
    ("If you could plan a surprise date night for us with unlimited budget, what happens?", "Dreams"),
    ("What is your favorite memory of us laughing until our stomachs hurt?", "Memories"),
    ("What is the most adventurous thing you'd be willing to do with me?", "Adventures"),
    ("What’s one book, movie, or show that you think we should experience together?", "Culture"),
    ("What is your love language, and how can I speak it better across the miles?", "Heart to Heart"),
    ("If you could bottle up one feeling from our time together, which would it be?", "Romantic"),
    ("What’s something you never get tired of talking to me about?", "Connection"),
    ("What makes you feel peaceful and grounded when life gets hectic?", "Deep"),
    ("What is your favorite nickname for me (or what would you like it to be)?", "Flirty"),
    ("What is the first thing we should do the second we meet at the airport/station?", "Romantic"),
    ("If we opened a cozy coffee shop together, what would it be named?", "Playful"),
    ("What is something you learned this week that surprised you?", "Connection"),
    ("What is your favorite childhood memory?", "Deep"),
    ("What’s something I do that makes you feel deeply respected and understood?", "Heart to Heart"),
    ("If you could send me a care package today, what three items would be inside?", "Care"),
    ("What is your favorite late-night conversation we’ve ever had?", "Memories"),
    ("What is one promise you make to me for our future?", "Romantic"),
    ("If you could freeze time during one moment we shared, which one would it be?", "Memories"),
    ("What is your favorite thing about our daily calls or texts?", "Connection"),
    ("What is a song that makes you want to dance around the living room?", "Fun"),
    ("What makes you feel happiest right now in this season of your life?", "Deep"),
    ("What are you most looking forward to about us finally being in the same place?", "Dreams"),
]


class Command(BaseCommand):
    help = "Initializes Jojo and Jay users, profiles, couple settings, and 65+ questions"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Setting up Our Space..."))

        # 1. Create or get Jojo
        jojo, created_jojo = User.objects.get_or_create(
            username='jojo',
            defaults={
                'first_name': 'Jojo',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        jojo.set_password('jojolove')
        jojo.save()
        if created_jojo:
            self.stdout.write(self.style.SUCCESS("Created user 'jojo' with password 'jojolove'"))
        else:
            self.stdout.write(self.style.SUCCESS("Updated user 'jojo' (password: 'jojolove')"))

        # Profile for Jojo
        jojo_profile, _ = UserProfile.objects.get_or_create(user=jojo)
        jojo_profile.display_name = 'Jojo'
        jojo_profile.city = 'Kampala'
        jojo_profile.timezone = 'Africa/Kampala'
        jojo_profile.avatar_emoji = '🌸'
        jojo_profile.wake_hour = 7
        jojo_profile.sleep_hour = 23
        jojo_profile.save()

        # 2. Create or get Jay
        jay, created_jay = User.objects.get_or_create(
            username='jay',
            defaults={
                'first_name': 'Jay',
                'is_staff': True,
            }
        )
        jay.set_password('jaylove')
        jay.save()
        if created_jay:
            self.stdout.write(self.style.SUCCESS("Created user 'jay' with password 'jaylove'"))
        else:
            self.stdout.write(self.style.SUCCESS("Updated user 'jay' (password: 'jaylove')"))

        # Profile for Jay
        jay_profile, _ = UserProfile.objects.get_or_create(user=jay)
        jay_profile.display_name = 'Jay'
        jay_profile.city = 'London'  # Editable in settings
        jay_profile.timezone = 'Europe/London'
        jay_profile.avatar_emoji = '💙'
        jay_profile.wake_hour = 7
        jay_profile.sleep_hour = 23
        jay_profile.save()

        # 3. Couple Settings
        settings = CoupleSettings.load()
        if not settings.anniversary_date:
            # Default anniversary: 1 year ago today
            settings.anniversary_date = timezone.localdate() - timedelta(days=365)
        if not settings.next_visit_date:
            # Default next visit: 45 days from today
            settings.next_visit_date = timezone.localdate() + timedelta(days=45)
        settings.next_visit_title = "Next time we hug 💕"
        settings.app_title = "Jojo & Jay's Space"
        settings.save()
        self.stdout.write(self.style.SUCCESS("Configured couple settings"))

        # 4. Seed Questions
        questions_created = 0
        for i, (text, cat) in enumerate(SEED_QUESTIONS, start=1):
            q, created = DailyQuestion.objects.get_or_create(
                day_number=i,
                defaults={
                    'question_text': text,
                    'category': cat,
                    'is_active': True,
                }
            )
            if created:
                questions_created += 1

        self.stdout.write(self.style.SUCCESS(f"Seeded {questions_created} new questions (total: {DailyQuestion.objects.count()})"))

        # 5. Add starter Love Note & starter Check-in if empty
        if not LoveNote.objects.exists():
            LoveNote.objects.create(
                author=jojo,
                content="Welcome to our little corner of the internet! Can't wait for all our memories here 🥰",
                color='pink',
                is_pinned=True
            )
            LoveNote.objects.create(
                author=jay,
                content="Counting down the days until I get to hold you again ✨",
                color='cream',
                is_pinned=True
            )
            self.stdout.write(self.style.SUCCESS("Added starter love notes"))

        if not DailyCheckIn.objects.exists():
            DailyCheckIn.objects.create(
                user=jojo,
                date=timezone.localdate(),
                mood_emoji="🥰",
                note="Setting up our new cozy home online!"
            )
            DailyCheckIn.objects.create(
                user=jay,
                date=timezone.localdate(),
                mood_emoji="✨",
                note="Excited to be sharing this space with you."
            )
            self.stdout.write(self.style.SUCCESS("Added starter check-ins"))

        # 6. Seed This or That questions
        this_or_that_data = [
            ("Morning coffee in bed", "Late night dessert together", "☕", "🍰", "Food & Cozy"),
            ("Cozy movie night inside", "Dressed-up date night out", "🎬", "👗", "Dates"),
            ("Beach holiday with sunsets", "Snowy cabin with a fireplace", "🏖️", "🏔️", "Getaways"),
            ("Cooking a new recipe together", "Ordering takeout and bingeing a show", "🍳", "🍕", "Food & Cozy"),
            ("FaceTime marathon until 2 AM", "Sweet voice note sent when waking up", "📱", "🎙️", "Long Distance"),
            ("Long scenic road trip", "Fast flight to get there sooner", "🚗", "✈️", "Travel"),
            ("Giving big spontaneous hugs", "Holding hands while walking", "🫂", "🤝", "Affection"),
            ("Silly banter & roasting each other", "Deep vulnerable late night talk", "😜", "🥹", "Connection"),
        ]
        for opt_a, opt_b, em_a, em_b, cat in this_or_that_data:
            ThisOrThat.objects.get_or_create(
                option_a=opt_a,
                option_b=opt_b,
                defaults={'emoji_a': em_a, 'emoji_b': em_b, 'category': cat}
            )

        # 7. Seed Songs
        if not Song.objects.exists():
            Song.objects.create(
                added_by=jojo,
                title="Lover",
                artist="Taylor Swift",
                url="https://open.spotify.com/track/1dGr1nsAZOsWiScoktAmhn",
                note="Always reminds me of dancing around the room with you 💕"
            )
            Song.objects.create(
                added_by=jay,
                title="Until I Found You",
                artist="Stephen Sanchez",
                url="https://open.spotify.com/track/0T5iIrXA4p5GsubkhuBIKV",
                note="This song is basically us ✨"
            )

        # 8. Seed Milestones
        if not Milestone.objects.exists():
            Milestone.objects.create(
                title="The Day We First Talked",
                date=timezone.localdate() - timedelta(days=450),
                description="The beginning of our favorite adventure.",
                emoji="💌"
            )
            Milestone.objects.create(
                title="Our Official Anniversary",
                date=settings.anniversary_date or (timezone.localdate() - timedelta(days=365)),
                description="When we made it official. Best decision ever.",
                emoji="💍"
            )
            Milestone.objects.create(
                title="First Airport Reunion Hug",
                date=timezone.localdate() - timedelta(days=180),
                description="Running towards each other through arrivals. Never wanted to let go.",
                emoji="✈️"
            )

        self.stdout.write(self.style.SUCCESS("\n🎉 Our Space setup complete!"))
        self.stdout.write(self.style.SUCCESS("Logins: 'jojo' (pw: jojolove) and 'jay' (pw: jaylove)"))
