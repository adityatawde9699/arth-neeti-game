from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from game_engine.services import GameEngine
import traceback

class Command(BaseCommand):
    help = 'Debugs the start_game process'

    def handle(self, *args, **options):
        self.stdout.write("Starting debug process...")
        try:
            # Get or create a test user
            user, created = User.objects.get_or_create(username='debug_user')
            if created:
                user.set_password('password')
                user.save()
            
            self.stdout.write(f"Using user: {user.username}")
            
            # Attempt to start session
            self.stdout.write("Calling GameEngine.start_new_session...")
            session = GameEngine.start_new_session(user)
            
            self.stdout.write(self.style.SUCCESS(f"Successfully started session ID: {session.id}"))
            self.stdout.write(f"Wealth: {session.wealth}")
            self.stdout.write(f"Persona: {session.persona_profile.career_stage}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR("FAILED to start session"))
            self.stdout.write(self.style.ERROR(str(e)))
            self.stdout.write(traceback.format_exc())
