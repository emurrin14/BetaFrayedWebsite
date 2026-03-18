from django.contrib import admin
from .models import Subscriber, Newsletter
from .tasks import send_bulk_newsletter_task

# 1. Register the Subscriber model so you can see your list
@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'date_subscribed')
    list_filter = ('is_active',) # Adds a sidebar filter

# 2. Define the custom action
@admin.action(description="Send selected newsletters via Celery")
def send_newsletter_action(modeladmin, request, queryset):
    # Loop through the newsletters checked by the user
    for newsletter in queryset:
        if not newsletter.was_sent:
            # Trigger the Celery task in the background!
            send_bulk_newsletter_task.delay(newsletter.id)
            
    # Show a green success message at the top of the admin screen
    modeladmin.message_user(request, "Your newsletters have been handed off to Celery and are sending in the background!")

# 3. Register the Newsletter model and attach the action
@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'was_sent')
    actions = [send_newsletter_action] # This adds it to the "Action" dropdown!