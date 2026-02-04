from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_engine', '0002_add_lifelines'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenariocard',
            name='title_hi',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='scenariocard',
            name='description_hi',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scenariocard',
            name='title_mr',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='scenariocard',
            name='description_mr',
            field=models.TextField(blank=True, null=True),
        ),
    ]
