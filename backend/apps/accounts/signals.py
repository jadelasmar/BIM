from django.contrib.auth.models import Group
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.conf import settings


DEFAULT_USER_GROUP = "Viewer"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def assign_default_viewer_group(sender, instance, created, **kwargs):
    if not created or instance.is_superuser or instance.groups.exists():
        return

    default_group, _ = Group.objects.get_or_create(name=DEFAULT_USER_GROUP)
    instance.groups.add(default_group)
