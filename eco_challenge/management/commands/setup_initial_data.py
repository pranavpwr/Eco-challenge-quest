from django.core.management.base import BaseCommand
from eco_challenge.models import Biome, EcoTask

class Command(BaseCommand):
    help = 'Sets up initial data for the Eco-Challenge Quest'

    def handle(self, *args, **kwargs):
        # Create initial biomes with progressive unlocking
        forest = Biome.objects.create(
            name='Forest',
            description='Begin your eco-journey by protecting and nurturing forest ecosystems. Complete tasks to earn 100 points and unlock the Ocean biome!',
            required_points=0,
            is_unlocked=True
        )

        ocean = Biome.objects.create(
            name='Ocean',
            description='Dive into marine conservation! Earn another 100 points to unlock the Desert biome and continue your environmental journey.',
            required_points=100,
            is_unlocked=False
        )

        desert = Biome.objects.create(
            name='Desert',
            description='Master desert conservation! Complete these challenges to become an elite eco-warrior with mastery over all biomes.',
            required_points=200,
            is_unlocked=False
        )

        # Forest Biome Tasks (Total: 100 points)
        forest_tasks = [
            {
                'title': 'Plant a Tree',
                'description': 'Plant a native tree species in your local area and document its growth for a week.',
                'points': 25,
                'difficulty': 'medium'
            },
            {
                'title': 'Start Composting',
                'description': 'Set up a home composting system and maintain it for 5 days.',
                'points': 20,
                'difficulty': 'easy'
            },
            {
                'title': 'Forest Clean-up',
                'description': 'Organize or participate in a local forest/park clean-up event.',
                'points': 30,
                'difficulty': 'hard'
            },
            {
                'title': 'Bird Feeder',
                'description': 'Create and maintain a bird feeder using recycled materials.',
                'points': 15,
                'difficulty': 'easy'
            },
            {
                'title': 'Native Plant Garden',
                'description': 'Start a small garden with native plant species that support local wildlife.',
                'points': 10,
                'difficulty': 'easy'
            }
        ]

        # Ocean Biome Tasks (Total: 100 points)
        ocean_tasks = [
            {
                'title': 'Beach Cleanup',
                'description': 'Organize or participate in a beach cleanup event and document the types of waste collected.',
                'points': 30,
                'difficulty': 'hard'
            },
            {
                'title': 'Plastic-Free Week',
                'description': 'Go without single-use plastics for a week and document your alternatives.',
                'points': 25,
                'difficulty': 'medium'
            },
            {
                'title': 'Sustainable Seafood',
                'description': 'Research and switch to sustainable seafood options for a week.',
                'points': 15,
                'difficulty': 'easy'
            },
            {
                'title': 'Water Conservation',
                'description': 'Implement water-saving practices at home and track your water usage.',
                'points': 20,
                'difficulty': 'medium'
            },
            {
                'title': 'Ocean Education',
                'description': 'Create an educational post about marine conservation and share it.',
                'points': 10,
                'difficulty': 'easy'
            }
        ]

        # Desert Biome Tasks (Total: 100 points)
        desert_tasks = [
            {
                'title': 'Xeriscaping Project',
                'description': 'Design and implement a water-efficient garden using desert plants.',
                'points': 35,
                'difficulty': 'hard'
            },
            {
                'title': 'Desert Wildlife Protection',
                'description': 'Research local desert wildlife and create a conservation awareness campaign.',
                'points': 25,
                'difficulty': 'medium'
            },
            {
                'title': 'Water Audit',
                'description': 'Conduct a household water audit and implement water-saving measures.',
                'points': 20,
                'difficulty': 'medium'
            },
            {
                'title': 'Solar Energy',
                'description': 'Calculate your home\'s solar potential and research solar options.',
                'points': 15,
                'difficulty': 'easy'
            },
            {
                'title': 'Desert Ecosystem Education',
                'description': 'Create an educational resource about desert ecosystem preservation.',
                'points': 5,
                'difficulty': 'easy'
            }
        ]

        # Create tasks for each biome
        for task in forest_tasks:
            EcoTask.objects.create(biome=forest, **task)
            self.stdout.write(f"Created forest task: {task['title']}")

        for task in ocean_tasks:
            EcoTask.objects.create(biome=ocean, **task)
            self.stdout.write(f"Created ocean task: {task['title']}")

        for task in desert_tasks:
            EcoTask.objects.create(biome=desert, **task)
            self.stdout.write(f"Created desert task: {task['title']}")

        self.stdout.write(self.style.SUCCESS('Successfully created initial data with balanced progression system')) 