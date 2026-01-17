"""
Cron jobs for CRM app.
"""
from django.utils import timezone
from .models import Product


def log_crm_heartbeat():
    """Log CRM system heartbeat every 5 minutes."""
    print(f"CRM Heartbeat: {timezone.now()}")


def update_low_stock():
    """Update low stock products every 12 hours."""
    low_stock = Product.objects.filter(stock__lt=10)
    for product in low_stock:
        product.stock += 10
        product.save()
    print(f"Updated {low_stock.count()} low stock products")
