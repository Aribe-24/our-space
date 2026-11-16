from django.db import migrations, models


def restore_jojo_and_shared_location(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('core', 'UserProfile')
    CoupleSettings = apps.get_model('core', 'CoupleSettings')

    jojo = User.objects.filter(username='jojo').first()
    jay = User.objects.filter(username='jay').first()
    if jojo:
        User.objects.filter(pk=jojo.pk).update(first_name='Jojo')
        UserProfile.objects.filter(user_id=jojo.pk).update(
            display_name='Jojo', city='Kampala', timezone='Africa/Kampala'
        )
    if jay:
        UserProfile.objects.filter(user_id=jay.pk).update(
            city='Kampala', timezone='Africa/Kampala'
        )
    CoupleSettings.objects.filter(pk=1).update(app_title="Jojo & Jay's Space")


class Migration(migrations.Migration):
    dependencies = [('core', '0004_doodle')]

    operations = [
        migrations.RunPython(restore_jojo_and_shared_location, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='couplesettings',
            name='app_title',
            field=models.CharField(default="Jojo & Jay's Space", max_length=120),
        ),
    ]
