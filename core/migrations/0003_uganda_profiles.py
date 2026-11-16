from django.db import migrations, models


def set_uganda_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('core', 'UserProfile')

    joan = User.objects.filter(username='jojo').first()
    if joan:
        UserProfile.objects.filter(user_id=joan.pk).update(
            display_name='Joan',
            city='Uganda',
            timezone='Africa/Kampala',
        )
        User.objects.filter(pk=joan.pk).update(first_name='Joan')

    jay = User.objects.filter(username='jay').first()
    if jay:
        UserProfile.objects.filter(user_id=jay.pk).update(
            city='Uganda',
            timezone='Africa/Kampala',
        )

    CoupleSettings = apps.get_model('core', 'CoupleSettings')
    CoupleSettings.objects.filter(pk=1).update(app_title="Joan & Jay's Space")


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_thisorthat_thisorthatvote'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(set_uganda_profiles, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='couplesettings',
            name='app_title',
            field=models.CharField(default="Joan & Jay's Space", max_length=120),
        ),
    ]
