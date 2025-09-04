from django.db import models
from secrets import token_urlsafe

class Links(models.Model):
    redirect_link = models.URLField()
    token = models.CharField(max_length=10, unique=True, null=True, blank=True)
    create_at = models.DateTimeField(auto_now_add=True)
    expiration_time = models.DateTimeField(null=True, blank=True)
    max_unique_cliques = models.PositiveBigIntegerField(null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.redirect_link
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = token_urlsafe(6)
            
        super().save(*args, **kwargs)