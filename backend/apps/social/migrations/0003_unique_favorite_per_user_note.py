# Generated manually - enforce one favorite per note per user

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("social", "0002_commentlike"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="favorite",
            unique_together={("user", "note")},
        ),
    ]
