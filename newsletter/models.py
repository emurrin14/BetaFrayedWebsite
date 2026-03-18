from django.db import models

# Create your models here.
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True) # Lets people unsubscribe without deleting them
    date_subscribed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email



class Newsletter(models.Model):
    subject = models.CharField(max_length=255)
    html_content = models.TextField(help_text="Write your HTML newsletter here.")
    created_at = models.DateTimeField(auto_now_add=True)
    was_sent = models.BooleanField(default=False, help_text="Tracks if this has been sent yet.")

    def __str__(self):
        return self.subject