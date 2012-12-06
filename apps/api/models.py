import hmac
import uuid
from hashlib import sha1

from django.contrib.auth.models import User
from django.db import models


class APIApp(models.Model):
    """APIApp Model."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    url = models.URLField(max_length=300, blank=True, default='')
    owner = models.ForeignKey(User)
    key = models.CharField(
        help_text='Leave this field empty to generate a new API key.',
        max_length=256, blank=True, default='')
    is_mozilla_app = models.BooleanField(blank=True, default=False)
    is_active = models.BooleanField(blank=True, default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        """Return unicode representation of object."""
        return "%s for %s" % (self.name, self.owner)

    def save(self, *args, **kwargs):
        """Generates a key if none and saves object."""
        if not self.key:
            self.key = self.generate_key()

        return super(APIApp, self).save(*args, **kwargs)

    def generate_key(self):
        """Return a key."""
        new_uuid = uuid.uuid4()
        return hmac.new(str(new_uuid), digestmod=sha1).hexdigest()
