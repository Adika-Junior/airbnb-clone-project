"""
Management command to create sample properties for testing.
"""
from django.core.management.base import BaseCommand
from apps.properties.models import Property
from apps.messaging.models import User
from decimal import Decimal
import random


class Command(BaseCommand):
    help = 'Create sample properties for testing and demonstration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of sample properties to create',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear all existing properties before creating new ones',
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']
        
        if clear:
            Property.objects.all().delete()
            self.stdout.write(self.style.WARNING('Deleted all existing properties.'))
        
        # Get or create a sample host
        host, created = User.objects.get_or_create(
            email='host@example.com',
            defaults={
                'first_name': 'Sample',
                'last_name': 'Host',
                'role': 'host',
                'password': 'pbkdf2_sha256$600000$dummy$dummy='  # Dummy password, users should use createsuperuser
            }
        )
        if created:
            host.set_password('samplepassword123')
            host.save()
            self.stdout.write(self.style.SUCCESS(f'Created sample host: {host.email}'))
        
        # Sample property data
        sample_properties = [
            {
                'title': 'Beautiful Beachfront Villa',
                'description': 'Stunning oceanfront property with panoramic views. Perfect for a relaxing vacation with modern amenities and beach access.',
                'property_type': 'villa',
                'price_per_night': Decimal('299.99'),
                'location': 'Miami Beach, FL',
                'city': 'Miami Beach',
                'country': 'USA',
                'bedrooms': 3,
                'bathrooms': 2,
                'beds': 3,
                'max_guests': 6,
                'wifi': True,
                'kitchen': True,
                'parking': True,
                'pool': True,
                'air_conditioning': True,
                'tv': True,
                'is_featured': True,
            },
            {
                'title': 'Cozy Downtown Apartment',
                'description': 'Modern apartment in the heart of the city. Close to restaurants, shops, and public transportation.',
                'property_type': 'apartment',
                'price_per_night': Decimal('89.99'),
                'location': 'New York, NY',
                'city': 'New York',
                'country': 'USA',
                'bedrooms': 1,
                'bathrooms': 1,
                'beds': 1,
                'max_guests': 2,
                'wifi': True,
                'kitchen': True,
                'air_conditioning': True,
                'heating': True,
                'tv': True,
            },
            {
                'title': 'Luxury Mountain Cabin',
                'description': 'Escape to this beautiful mountain retreat. Perfect for hiking, skiing, and enjoying nature.',
                'property_type': 'house',
                'price_per_night': Decimal('199.99'),
                'location': 'Aspen, CO',
                'city': 'Aspen',
                'country': 'USA',
                'bedrooms': 4,
                'bathrooms': 3,
                'beds': 5,
                'max_guests': 8,
                'wifi': True,
                'kitchen': True,
                'parking': True,
                'heating': True,
                'tv': True,
                'washer': True,
                'dryer': True,
                'is_featured': True,
            },
            {
                'title': 'Modern Studio in Paris',
                'description': 'Charming studio apartment with Eiffel Tower view. Perfect for a romantic getaway in the City of Light.',
                'property_type': 'studio',
                'price_per_night': Decimal('149.99'),
                'location': 'Paris, France',
                'city': 'Paris',
                'country': 'France',
                'bedrooms': 0,
                'bathrooms': 1,
                'beds': 1,
                'max_guests': 2,
                'wifi': True,
                'kitchen': True,
                'air_conditioning': False,
                'heating': True,
                'tv': True,
            },
            {
                'title': 'Spacious Family House',
                'description': 'Large family home with backyard, perfect for families with children. Safe neighborhood with parks nearby.',
                'property_type': 'house',
                'price_per_night': Decimal('179.99'),
                'location': 'Austin, TX',
                'city': 'Austin',
                'country': 'USA',
                'bedrooms': 5,
                'bathrooms': 3,
                'beds': 6,
                'max_guests': 10,
                'wifi': True,
                'kitchen': True,
                'parking': True,
                'pool': True,
                'air_conditioning': True,
                'heating': True,
                'tv': True,
                'washer': True,
                'dryer': True,
            },
            {
                'title': 'Elegant Condo with City View',
                'description': 'Luxurious condo with stunning city skyline views. Modern design with premium finishes.',
                'property_type': 'condo',
                'price_per_night': Decimal('249.99'),
                'location': 'Los Angeles, CA',
                'city': 'Los Angeles',
                'country': 'USA',
                'bedrooms': 2,
                'bathrooms': 2,
                'beds': 2,
                'max_guests': 4,
                'wifi': True,
                'kitchen': True,
                'parking': True,
                'pool': True,
                'air_conditioning': True,
                'tv': True,
                'washer': True,
                'dryer': True,
                'is_featured': True,
            },
            {
                'title': 'Charming Cottage by the Lake',
                'description': 'Quaint lakeside cottage perfect for fishing, boating, and relaxation. Peaceful and serene setting.',
                'property_type': 'house',
                'price_per_night': Decimal('129.99'),
                'location': 'Lake Tahoe, CA',
                'city': 'Lake Tahoe',
                'country': 'USA',
                'bedrooms': 2,
                'bathrooms': 1,
                'beds': 2,
                'max_guests': 4,
                'wifi': True,
                'kitchen': True,
                'parking': True,
                'tv': True,
            },
            {
                'title': 'Rooftop Apartment in Brooklyn',
                'description': 'Stylish rooftop apartment with amazing views of Manhattan. Close to subway and local attractions.',
                'property_type': 'apartment',
                'price_per_night': Decimal('159.99'),
                'location': 'Brooklyn, NY',
                'city': 'Brooklyn',
                'country': 'USA',
                'bedrooms': 2,
                'bathrooms': 1,
                'beds': 2,
                'max_guests': 4,
                'wifi': True,
                'kitchen': True,
                'air_conditioning': True,
                'heating': True,
                'tv': True,
            },
            {
                'title': 'Tropical Island Bungalow',
                'description': 'Beautiful bungalow steps from pristine beaches. Perfect tropical getaway with ocean breezes.',
                'property_type': 'house',
                'price_per_night': Decimal('219.99'),
                'location': 'Hawaii, HI',
                'city': 'Honolulu',
                'country': 'USA',
                'bedrooms': 3,
                'bathrooms': 2,
                'beds': 3,
                'max_guests': 6,
                'wifi': True,
                'kitchen': True,
                'parking': True,
                'air_conditioning': True,
                'tv': True,
                'is_featured': True,
            },
            {
                'title': 'Historic Downtown Loft',
                'description': 'Converted warehouse loft in historic district. High ceilings, exposed brick, and modern amenities.',
                'property_type': 'apartment',
                'price_per_night': Decimal('139.99'),
                'location': 'Portland, OR',
                'city': 'Portland',
                'country': 'USA',
                'bedrooms': 1,
                'bathrooms': 1,
                'beds': 1,
                'max_guests': 2,
                'wifi': True,
                'kitchen': True,
                'parking': True,
                'air_conditioning': True,
                'heating': True,
                'tv': True,
            },
        ]
        
        created_count = 0
        for i, prop_data in enumerate(sample_properties[:count]):
            # Add some variation to prices
            base_price = float(prop_data['price_per_night'])
            varied_price = Decimal(str(base_price + random.uniform(-20, 20)))
            
            property_obj = Property.objects.create(
                host=host,
                title=prop_data['title'],
                description=prop_data['description'],
                property_type=prop_data['property_type'],
                price_per_night=max(varied_price, Decimal('50.00')),  # Minimum price
                location=prop_data['location'],
                city=prop_data.get('city', ''),
                country=prop_data.get('country', ''),
                bedrooms=prop_data['bedrooms'],
                bathrooms=prop_data['bathrooms'],
                beds=prop_data['beds'],
                max_guests=prop_data['max_guests'],
                wifi=prop_data.get('wifi', False),
                kitchen=prop_data.get('kitchen', False),
                parking=prop_data.get('parking', False),
                pool=prop_data.get('pool', False),
                air_conditioning=prop_data.get('air_conditioning', False),
                heating=prop_data.get('heating', False),
                tv=prop_data.get('tv', False),
                washer=prop_data.get('washer', False),
                dryer=prop_data.get('dryer', False),
                is_featured=prop_data.get('is_featured', False),
                image_url=prop_data.get('image_url', ''),
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created property: {property_obj.title} - ${property_obj.price_per_night}/night')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'\nSuccessfully created {created_count} sample properties!')
        )
        self.stdout.write(
            self.style.WARNING(f'\nNote: To access the host account, use email: host@example.com')
        )
