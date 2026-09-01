from django.db import migrations


# on first migrate, admin1/admin1 must exist as the bootstrap admin.
# data migration only runs once
def create_admin1(apps, schema_editor):
    User = apps.get_model('register', 'CustomUser')
    if User.objects.filter(username='admin1').exists():
        return  # already there, nothing to do

    # apps.get_model gives a historical model so set_password isn't on it.
    # import make_password from django.contrib.auth.hashers
    from django.contrib.auth.hashers import make_password
    User.objects.create(
        username='admin1',
        password=make_password('admin1'),
        email='admin1@example.com',
        first_name='Admin',
        last_name='One',
        is_staff=True,
        is_superuser=True,
        is_active=True,
        currency='GBP',
        balance=0,
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('register', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin1, noop),
    ]
