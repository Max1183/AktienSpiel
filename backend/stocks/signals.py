from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Team, UserProfile


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        team, created = Team.objects.get_or_create(name="default")
        UserProfile.objects.create(user=instance, team=team)
