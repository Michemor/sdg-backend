import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from impact_tracker.models import (
    SDGGoal, Department, Researcher, Activity, BenchmarkInstitution
)
from django.db import transaction

class Command(BaseCommand):
    help = 'Seeds the database with realistic mock data for the SDG Impact Dashboard.'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Starting database seeding...')
        
        # Clean up existing data
        self.stdout.write('Clearing old data...')
        User.objects.filter(is_superuser=False).delete()
        Department.objects.all().delete()
        Researcher.objects.all().delete()
        Activity.objects.all().delete()
        SDGGoal.objects.all().delete()
        BenchmarkInstitution.objects.all().delete()

        # 1. Create SDGs
        self.stdout.write('Creating SDGs...')
        sdgs_data = [
            (1, 'No Poverty', '#E5243B'),
            (2, 'Zero Hunger', '#DDA63A'),
            (3, 'Good Health and Well-being', '#4C9F38'),
            (4, 'Quality Education', '#C5192D'),
            (5, 'Gender Equality', '#FF3A21'),
            (6, 'Clean Water and Sanitation', '#26BDE2'),
            (7, 'Affordable and Clean Energy', '#FCC30B'),
            (8, 'Decent Work and Economic Growth', '#A21942'),
            (9, 'Industry, Innovation and Infrastructure', '#FD6925'),
            (10, 'Reduced Inequality', '#DD1367'),
            (11, 'Sustainable Cities and Communities', '#FD9D24'),
            (12, 'Responsible Consumption and Production', '#BF8B2E'), 
            (13, 'Climate Action', '#3F7E44'),
            (14, 'Life Below Water', '#0A97D9'),
            (15, 'Life on Land', '#56C02B'),
            (16, 'Peace, Justice and Strong Institutions', '#00689D'),
            (17, 'Partnerships for the Goals', '#19486A'),
        ]
        sdgs = []
        for number, name, color in sdgs_data:
            sdg = SDGGoal.objects.create(number=number, name=name, color_code=color, description=f"Description for {name}")
            sdgs.append(sdg)

        # 2. Create Departments
        self.stdout.write('Creating Departments...')
        department_names = ['Computer Science', 'Theology and Biblical Studies', 'Nursing', 'Communication Studies', 'School of Business and Economics']
        departments = [Department.objects.create(name=name) for name in department_names]

        # 3. Create Users and Researchers
        self.stdout.write('Creating Users and Researchers...')
        researchers = []
        first_names = ['Jane', 'John', 'Peter', 'Mary', 'David', 'Susan', 'Michael', 'Sarah']
        last_names = ['Doe', 'Smith', 'Jones', 'Williams', 'Brown', 'Davis', 'Miller', 'Wilson']
        for i in range(10):
            username = f'researcher{i+1}'
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            user, created = User.objects.get_or_create(username=username, defaults={'first_name': first_name, 'last_name': last_name, 'email': f'{username}@daystar.ac.ke'})
            if created:
                user.set_password('password')
                user.save()
            
            researcher = Researcher.objects.create(
                user=user,
                department=random.choice(departments),
                title=random.choice(['Professor', 'Lecturer', 'Associate Professor', 'Research Fellow'])
            )
            researchers.append(researcher)

        # 4. Create Activities
        self.stdout.write('Creating Activities...')
        activity_titles = [
            'AI-Powered Mosquito-borne Disease Prediction in Kisumu County',
            'The Role of Digital Media in Shaping Ethical Frameworks in Kenya',
            'Sustainable Agribusiness Models for Youth Empowerment in Rural Kenya',
            'Improving Maternal Health Outcomes through Mobile Clinics in Narok',
            'The Impact of Microfinance on Female Entrepreneurs in Nairobi Slums',
            'A Theological Perspective on Climate Change and Creation Care in Africa',
            'Developing Low-Cost Water Purification Systems for Arid and Semi-Arid Lands',
            'Curriculum Reforms for Enhancing SDG-focused Education in Kenyan Universities',
            'Analysis of Post-Harvest Losses in the Kenyan Maize Value Chain',
            'Cybersecurity Challenges for SMEs in the Digital Economy',
            'Peacebuilding and Conflict Resolution Mechanisms in Pastoralist Communities',
            'Theological Ethics and Corporate Social Responsibility',
            'The Nursing Profession and its Role in achieving SDG 3 in Kenya',
            'Bridging the Digital Divide: A Study of Community Networks',
            'Renewable Energy Adoption Barriers in Kenyan Households'
        ]
        for i in range(50):
            activity = Activity.objects.create(
                title=random.choice(activity_titles) + f" - Study #{i+1}",
                description=f"This is a detailed description for activity #{i+1}.",
                impact_summary=f"This is the impact summary for activity #{i+1}.",
                activity_type=random.choice(['Project', 'Publication']),
                status=random.choice(['Active', 'Completed', 'Published']),
                author=random.choice(researchers),
                original_publication_date=f'202{random.randint(0, 4)}-{random.randint(1, 12)}-{random.randint(1, 28)}'
            )
            # Link to 1-3 random SDGs
            activity.sdgs.set(random.sample(sdgs, k=random.randint(1, 3)))

        # 5. Create Benchmark Institutions
        self.stdout.write('Creating Benchmark Institutions...')
        benchmark_data = [
            {'name': 'Strathmore University', 'total_sdg_score': 150, 'projects_count': 80, 'publications_count': 250},
            {'name': 'University of Nairobi', 'total_sdg_score': 200, 'projects_count': 120, 'publications_count': 400},
            {'name': 'Kenyatta University', 'total_sdg_score': 180, 'projects_count': 100, 'publications_count': 350},
        ]
        for data in benchmark_data:
            BenchmarkInstitution.objects.create(**data)


        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
