from django.core.management.base import BaseCommand
from eco_challenge.models import Biome, EcoTask

class Command(BaseCommand):
    help = 'Creates initial biomes and tasks'

    def handle(self, *args, **kwargs):
        # Delete existing biomes and tasks
        Biome.objects.all().delete()
        EcoTask.objects.all().delete()

        # Create Forest Biome
        forest = Biome.objects.create(
            name="Forest",
            description="Begin your eco-journey in the forest ecosystem. Learn about conservation and biodiversity.",
            icon_class="fa-tree",
            required_points=0,
            is_unlocked=True
        )

        # Forest Tasks
        forest_tasks = [
            {
                "title": "Plant a Tree",
                "description": "Plant and nurture a tree sapling in your local area",
                "points": 30
            },
            {
                "title": "Forest Clean-up",
                "description": "Organize a forest clean-up activity",
                "points": 25
            },
            {
                "title": "Wildlife Documentation",
                "description": "Document local forest wildlife",
                "points": 35
            },
            {
                "title": "Seed Collection",
                "description": "Collect and preserve native tree seeds",
                "points": 20
            },
            {
                "title": "Forest Education",
                "description": "Create awareness about forest conservation",
                "points": 40
            }
        ]

        # Create Ocean Biome
        ocean = Biome.objects.create(
            name="Ocean",
            description="Explore marine conservation and protect our oceans.",
            icon_class="fa-water",
            required_points=100,
            is_unlocked=False
        )

        # Ocean Tasks
        ocean_tasks = [
            {
                "title": "Beach Clean-up",
                "description": "Organize a beach cleaning activity",
                "points": 45
            },
            {
                "title": "Plastic-Free Week",
                "description": "Avoid single-use plastics for a week",
                "points": 50
            },
            {
                "title": "Marine Education",
                "description": "Create awareness about marine conservation",
                "points": 40
            },
            {
                "title": "Water Conservation",
                "description": "Implement water-saving measures",
                "points": 35
            },
            {
                "title": "Ocean Awareness",
                "description": "Share information about ocean pollution",
                "points": 55
            }
        ]

        # Create Mountain Biome
        mountain = Biome.objects.create(
            name="Mountain",
            description="Preserve mountain ecosystems and wildlife.",
            icon_class="fa-mountain",
            required_points=250,
            is_unlocked=False
        )

        # Mountain Tasks
        mountain_tasks = [
            {
                "title": "Trail Maintenance",
                "description": "Help maintain mountain trails",
                "points": 60
            },
            {
                "title": "Alpine Research",
                "description": "Study mountain ecosystems",
                "points": 65
            },
            {
                "title": "Conservation Project",
                "description": "Join mountain conservation efforts",
                "points": 70
            },
            {
                "title": "Climate Impact",
                "description": "Document climate change effects",
                "points": 75
            },
            {
                "title": "Mountain Safety",
                "description": "Create mountain safety guidelines",
                "points": 80
            }
        ]

        # Create Urban Biome
        urban = Biome.objects.create(
            name="Urban",
            description="Transform city spaces into sustainable environments.",
            icon_class="fa-city",
            required_points=500,
            is_unlocked=False
        )

        # Urban Tasks
        urban_tasks = [
            {
                "title": "Community Garden",
                "description": "Start an urban garden project",
                "points": 85
            },
            {
                "title": "Green Transport",
                "description": "Use eco-friendly transportation",
                "points": 90
            },
            {
                "title": "Waste Management",
                "description": "Implement recycling system",
                "points": 95
            },
            {
                "title": "Energy Efficiency",
                "description": "Conduct home energy audit",
                "points": 100
            },
            {
                "title": "Urban Wildlife",
                "description": "Create urban wildlife habitats",
                "points": 105
            }
        ]

        # Function to create tasks
        def create_tasks(tasks_list, biome):
            for task in tasks_list:
                EcoTask.objects.create(
                    title=task["title"],
                    description=task["description"],
                    points=task["points"],
                    biome=biome
                )

        # Create all tasks
        create_tasks(forest_tasks, forest)
        create_tasks(ocean_tasks, ocean)
        create_tasks(mountain_tasks, mountain)
        create_tasks(urban_tasks, urban)

        self.stdout.write(self.style.SUCCESS('Successfully created all biomes and tasks!'))
