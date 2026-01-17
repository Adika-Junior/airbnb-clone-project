from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Listing(models.Model):
    """Travel listing model (can be used for experiences/activities)"""
    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='listings',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    location = models.CharField(max_length=200)
    image_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Booking(models.Model):
    """Booking model for properties and travel listings"""
    BOOKING_STATUS = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    # Can book either a property or a listing
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True,
        blank=True
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='bookings',
        null=True,
        blank=True
    )
    
    # Guest information (can be anonymous)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text='Logged-in user (null for anonymous booking)'
    )
    guest_name = models.CharField(max_length=200, help_text='Required for anonymous bookings')
    guest_email = models.EmailField(help_text='Required for anonymous bookings')
    guest_phone = models.CharField(max_length=20, blank=True)
    
    # Booking details
    check_in = models.DateField()
    check_out = models.DateField()
    guests = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='pending')
    special_requests = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['property', 'check_in', 'check_out']),
            models.Index(fields=['listing', 'check_in', 'check_out']),
        ]

    def __str__(self):
        item = self.property.title if self.property else self.listing.title
        guest = self.user.get_full_name() if self.user else self.guest_name
        return f"Booking for {item} by {guest} - {self.status}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.property and not self.listing:
            raise ValidationError('Booking must have either a property or listing')
        if self.property and self.listing:
            raise ValidationError('Booking cannot have both property and listing')
        if not self.user and (not self.guest_name or not self.guest_email):
            raise ValidationError('Anonymous bookings require guest_name and guest_email')
