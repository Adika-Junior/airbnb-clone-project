import logging
from django.core.cache import cache
from django_redis import get_redis_connection
from .models import Property

logger = logging.getLogger('properties')


def get_all_properties():
    """
    Retrieve all properties from cache or database.
    Uses low-level caching API to cache queryset for 1 hour.
    """
    cached_properties = cache.get('all_properties')
    
    if cached_properties is None:
        # Cache miss - fetch from database
        properties = list(Property.objects.all())
        # Cache for 1 hour (3600 seconds)
        cache.set('all_properties', properties, 3600)
        logger.info('Cache miss: Fetched properties from database')
        return properties
    
    # Cache hit
    logger.info('Cache hit: Retrieved properties from cache')
    return cached_properties


def get_redis_cache_metrics():
    """
    Retrieve and analyze Redis cache hit/miss metrics.
    Returns a dictionary with cache statistics.
    """
    try:
        redis_conn = get_redis_connection("default")
        info = redis_conn.info('stats')
        
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        
        total_requests = keyspace_hits + keyspace_misses
        
        hit_ratio = keyspace_hits / total_requests if total_requests > 0 else 0
        
        metrics = {
            'keyspace_hits': keyspace_hits,
            'keyspace_misses': keyspace_misses,
            'total_requests': total_requests,
            'hit_ratio': hit_ratio,
            'hit_percentage': round(hit_ratio * 100, 2)
        }
        
        logger.info(
            f"Cache Metrics - Hits: {keyspace_hits}, "
            f"Misses: {keyspace_misses}, "
            f"Hit Ratio: {hit_ratio:.2%}"
        )
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error retrieving cache metrics: {str(e)}")
        return {
            'error': str(e),
            'keyspace_hits': 0,
            'keyspace_misses': 0,
            'total_requests': 0,
            'hit_ratio': 0.0,
            'hit_percentage': 0.0
        }
