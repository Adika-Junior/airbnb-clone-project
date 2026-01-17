from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class Property(models.Model):
    """Property listing model with host, amenities, and images"""
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('condo', 'Condo'),
        ('villa', 'Villa'),
        ('studio', 'Studio'),
        ('other', 'Other'),
    ]
    
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
        null=True,
        blank=True,
        help_text='Host who owns this property'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES, default='apartment')
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=Decimal('0.00'),
        help_text='Price per night in USD'
    )
    location = models.CharField(max_length=200)
    address = models.TextField(blank=True, help_text='Full address')
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Property details
    bedrooms = models.PositiveIntegerField(default=1)
    bathrooms = models.PositiveIntegerField(default=1)
    beds = models.PositiveIntegerField(default=1)
    max_guests = models.PositiveIntegerField(default=2)
    square_feet = models.PositiveIntegerField(null=True, blank=True)
    
    # Amenities
    wifi = models.BooleanField(default=False)
    kitchen = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    air_conditioning = models.BooleanField(default=False)
    heating = models.BooleanField(default=False)
    tv = models.BooleanField(default=False)
    washer = models.BooleanField(default=False)
    dryer = models.BooleanField(default=False)
    
    # Images
    image = models.ImageField(upload_to='properties/', null=True, blank=True)
    image_url = models.URLField(blank=True, help_text='External image URL if not uploading')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    @property
    def average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'] or 0, 2)
        return 0.0
    
    @property
    def review_count(self):
        """Get count of approved reviews"""
        return self.reviews.filter(is_approved=True).count()
    
    @property
    def display_price(self):
        """Get formatted price"""
        return f"${self.price_per_night:.2f}"
    
    # Backward compatibility property for old 'price' field
    @property
    def price(self):
        """Backward compatibility - returns price_per_night"""
        return self.price_per_night

    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at', '-is_featured']
        indexes = [
            models.Index(fields=['host', 'is_active']),
            models.Index(fields=['location', 'is_active']),
            models.Index(fields=['property_type', 'is_active']),
        ]


class Review(models.Model):
    """Review model for properties"""
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        help_text='User who wrote the review (null for anonymous)'
    )
    guest_name = models.CharField(max_length=200, blank=True, help_text='Name for anonymous reviews')
    guest_email = models.EmailField(blank=True, help_text='Email for anonymous reviews')
    
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    comment = models.TextField(help_text='Review comment')
    
    # Moderation
    is_approved = models.BooleanField(default=True, help_text='Approved reviews are visible')
    is_anonymous = models.BooleanField(default=False, help_text='Anonymous review')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        reviewer = self.user.get_full_name() if self.user else self.guest_name or 'Anonymous'
        return f"Review by {reviewer} for {self.property.title} - {self.rating} stars"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'is_approved']),
            models.Index(fields=['user', 'created_at']),
        ]
        unique_together = [['property', 'user']]  # One review per user per property