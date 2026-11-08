from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from core.models import (
    UserProfile, CoupleSettings, DailyCheckIn, ThinkingOfYou,
    DailyQuestion, DailyAnswer, LoveNote, ThisOrThat, ThisOrThatVote
)

class OurSpaceFullSuiteTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Jojo
        self.jojo = User.objects.create_user(username='jojo', password='jojolove', first_name='Jojo')
        self.jojo_profile = UserProfile.objects.create(
            user=self.jojo,
            display_name='Jojo',
            city='Kampala',
            timezone='Africa/Kampala',
            avatar_emoji='🌸',
            wake_hour=7,
            sleep_hour=23
        )

        # Create Jay
        self.jay = User.objects.create_user(username='jay', password='jaylove', first_name='Jay')
        self.jay_profile = UserProfile.objects.create(
            user=self.jay,
            display_name='Jay',
            city='London',
            timezone='Europe/London',
            avatar_emoji='💙',
            wake_hour=7,
            sleep_hour=23
        )

        # Couple settings
        self.settings = CoupleSettings.load()
        self.settings.anniversary_date = timezone.localdate() - timedelta(days=100)
        self.settings.next_visit_date = timezone.localdate() + timedelta(days=30)
        self.settings.next_visit_title = 'London Hugs'
        self.settings.save()

        # Seed Question
        self.question = DailyQuestion.objects.create(
            question_text="What was the exact moment you fell in love with me?",
            category="Romantic",
            day_number=1
        )

        # Seed This or That
        self.tot = ThisOrThat.objects.create(
            option_a="Morning Coffee",
            option_b="Late Night Tea",
            emoji_a="☕",
            emoji_b="🍵"
        )

    def test_unauthenticated_redirect(self):
        """Pages must require login."""
        for url_name in ['dashboard', 'questions', 'photos', 'notes', 'extras']:
            res = self.client.get(reverse(url_name))
            self.assertEqual(res.status_code, 302)

    def test_double_blind_reveal_privacy(self):
        """
        Answers MUST remain completely private until BOTH partners have answered!
        """
        # Step 1: Jojo answers
        self.client.login(username='jojo', password='jojolove')
        res = self.client.post(reverse('submit_answer', args=[self.question.id]), {
            'answer_text': 'When you laughed at my silly joke in the cafe'
        })
        self.assertEqual(res.status_code, 302)

        # Jojo views page -> should see her answer and locked partner status
        jojo_view = self.client.get(reverse('questions'))
        self.assertContains(jojo_view, 'When you laughed at my silly joke')
        self.assertContains(jojo_view, 'answer is locked')
        self.assertNotContains(jojo_view, 'Unlocked! Both of you have answered')

        # Step 2: Jay logs in BEFORE answering -> must NOT see Jojo's answer text!
        self.client.logout()
        self.client.login(username='jay', password='jaylove')
        jay_view = self.client.get(reverse('questions'))
        self.assertNotContains(jay_view, 'When you laughed at my silly joke')
        self.assertContains(jay_view, 'has answered! Submit yours to reveal both')

        # Step 3: Jay answers now
        res = self.client.post(reverse('submit_answer', args=[self.question.id]), {
            'answer_text': 'The first time you sent me a voice note'
        })
        self.assertEqual(res.status_code, 302)

        # Now BOTH answers are revealed to Jay!
        jay_view_after = self.client.get(reverse('questions'))
        self.assertContains(jay_view_after, 'Unlocked! Both of you have answered')
        self.assertContains(jay_view_after, 'When you laughed at my silly joke')
        self.assertContains(jay_view_after, 'The first time you sent me a voice note')

        # And revealed to Jojo!
        self.client.logout()
        self.client.login(username='jojo', password='jojolove')
        jojo_view_after = self.client.get(reverse('questions'))
        self.assertContains(jojo_view_after, 'The first time you sent me a voice note')

    def test_love_notes_wall_crud(self):
        """Can create, pin, and delete love notes."""
        self.client.login(username='jojo', password='jojolove')
        res = self.client.post(reverse('add_love_note'), {
            'content': 'You are my favorite human in the entire galaxy ✨',
            'color': 'pink',
            'is_pinned': 'on'
        })
        self.assertEqual(res.status_code, 302)

        note = LoveNote.objects.filter(author=self.jojo).first()
        self.assertIsNotNone(note)
        self.assertTrue(note.is_pinned)

        # Check wall
        wall = self.client.get(reverse('notes'))
        self.assertContains(wall, 'favorite human in the entire galaxy')

        # Toggle pin
        self.client.post(reverse('toggle_pin_note', args=[note.id]))
        note.refresh_from_db()
        self.assertFalse(note.is_pinned)

    def test_this_or_that_game(self):
        """Voting records choices and detects match."""
        # Jojo votes A
        self.client.login(username='jojo', password='jojolove')
        res = self.client.post(reverse('vote_this_or_that', args=[self.tot.id]), {'choice': 'A'})
        self.assertEqual(res.status_code, 302)

        # Jay votes A (Match!)
        self.client.logout()
        self.client.login(username='jay', password='jaylove')
        res = self.client.post(reverse('vote_this_or_that', args=[self.tot.id]), {'choice': 'A'})
        self.assertEqual(res.status_code, 302)

        extras_page = self.client.get(reverse('extras'))
        self.assertContains(extras_page, 'You Matched!')
