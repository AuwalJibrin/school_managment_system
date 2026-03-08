from django.core.management.base import BaseCommand
from results.models import Subject, Term, Session

class Command(BaseCommand):
    help = 'Seeds the database with specific Subjects and Terms'

    def handle(self, *args, **kwargs):
        # Desired Subjects
        subjects_data = [
            {'name': 'maths', 'code': 'MTH'},
            {'name': 'english', 'code': 'ENG'},
            {'name': 'chemistry', 'code': 'CHM'},
            {'name': 'physic', 'code': 'PHY'},
        ]

        # Desired Terms
        terms_data = ['frist', 'secound', 'thrid']

        # Determine safe removal - we only want these elements. 
        # (Be careful if results already exist tied to other subjects/terms!)
        self.stdout.write('Clearing existing Subjects and Terms...')
        Subject.objects.all().delete()
        Term.objects.all().delete()
        # Session should generally be dynamic but we need at least one for Terms
        session, created = Session.objects.get_or_create(
            name='2024/2025',
            defaults={'is_active': True}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created Session {session.name}'))

        # Create Subjects
        for subject_info in subjects_data:
            subj, created = Subject.objects.get_or_create(
                name=subject_info['name'],
                defaults={'code': subject_info['code']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Subject {subj.name}'))

        # Create Terms
        for term_name in terms_data:
            trm, created = Term.objects.get_or_create(
                name=term_name,
                session=session
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created Term {trm.name}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded Subjects and Terms!'))
