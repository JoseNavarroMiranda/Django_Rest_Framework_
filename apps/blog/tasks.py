from celery import shared_task

import logging

from .models import PostAnalitics


logger = logging.getLogger(__name__)


#Definicion de tarea, utilizando @shared_task

@shared_task
def increment_post_impressions(post_id):
    """Icrementa las impresiones del post asociado"""
    try:
        analitics, created = PostAnalitics.objects.get_or_create(post__id=post_id)
        analitics.increment_impression()
    except Exception as e:
        logger.info(f"Error incrementing impressions for Post ID {post_id}: {str(e)}")