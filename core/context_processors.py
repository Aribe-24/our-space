from django.contrib.auth.models import User
from .models import CoupleSettings, UserProfile, ThinkingOfYou

def couple_context(request):
    """
    Context processor that supplies couple settings and partner information
    to all rendered templates.
    """
    context = {
        'couple_settings': CoupleSettings.load(),
        'partner_user': None,
        'partner_profile': None,
        'my_profile': None,
        'unread_tap': None,
    }

    if request.user.is_authenticated:
        # Fetch current user profile
        try:
            context['my_profile'] = request.user.profile
        except UserProfile.DoesNotExist:
            context['my_profile'] = None

        # Fetch partner (the other registered user)
        partner = User.objects.exclude(id=request.user.id).first()
        if partner:
            context['partner_user'] = partner
            try:
                context['partner_profile'] = partner.profile
            except UserProfile.DoesNotExist:
                context['partner_profile'] = None

        # Check for unread 'Thinking of You' taps
        latest_tap = ThinkingOfYou.objects.filter(
            receiver=request.user,
            viewed=False
        ).order_by('-created_at').first()
        if latest_tap:
            context['unread_tap'] = latest_tap

    return context
