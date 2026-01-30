from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_engine', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='lifelines',
            field=models.IntegerField(default=3),
        ),
    ]
