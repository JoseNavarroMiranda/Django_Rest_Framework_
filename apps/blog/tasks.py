from celery import shared_task

import logging
import redis
from .models import Post, PostAnalitics

from django.conf import settings

logger = logging.getLogger(__name__)

redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=6379, db=0)

#Definicion de tarea, utilizando @shared_task

@shared_task
def increment_post_impressions(post_id):
    """Icrementa las impresiones del post asociado"""
    try:
        analitics, created = PostAnalitics.objects.get_or_create(post__id=post_id)
        analitics.increment_impression()
    except Exception as e:
        logger.info(f"Error incrementing impressions for Post ID {post_id}: {str(e)}")


@shared_task
def increment_posts_views_task(slug , ip_address):
    """Icrementa las vistas de un post"""
    try:
        post = Post.objects.get(slug=slug)
        post_analitics, _ = PostAnalitics.objects.get_or_create(post=post)
        post_analitics.increment_impression()
    except Exception as e:
        logger.info(f"Error incrementing views for post slug {slug}, {str(e)}")
    
        

@shared_task
def sync_impressions_to_db():
    """sincronizar las impresiones almancenadas en redis con la base de datos"""
    keys = redis_client.keys("post:impressions:*")
    for key in keys:
        try:
            post_id = key.decode("utf-8").split(":")[-1]
            impressions = int(redis_client.get(key))
            
            analitics, _ = PostAnalitics.objects.get_or_create(post__id=post_id)
            analitics.impressions += impressions
            analitics.save()
            
            analitics._update_click_through_rate()
            
            redis_client.delete(key)
        except Exception as e:
            logger.info(f"Error syncing impressions for {key}: {str(e)}")