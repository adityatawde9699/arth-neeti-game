from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_engine', '0012_choice_feedback_hi_choice_feedback_mr_choice_text_hi_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gamesession',
            name='gameplay_log',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='gamesession',
            name='final_report',
            field=models.TextField(blank=True, default=''),
        ),
    ]
