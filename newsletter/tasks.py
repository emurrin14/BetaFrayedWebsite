from celery import shared_task
from mailersend import MailerSendClient, EmailBuilder
from django.conf import settings
from django.utils.html import strip_tags
from .models import Newsletter, Subscriber
import time

@shared_task
def send_bulk_newsletter_task(newsletter_id):
    try:
        # 1. Get the newsletter
        newsletter = Newsletter.objects.get(id=newsletter_id)
        
        # 2. Get ONLY active subscribers
        subscribers = Subscriber.objects.filter(is_active=True) 
        
        # 3. Initialize the modern v2 client
        ms = MailerSendClient(settings.MAILERSEND_API_KEY)
        success_count = 0
        
        # 4. Loop through and send individually
        for subscriber in subscribers:
            
            # Create a plain-text fallback version from your HTML
            plain_text_content = strip_tags(newsletter.html_content)
            
            # Build the email
            email = (
                EmailBuilder()
                .from_email("newsletter@test-ywj2lpnk531g7oqz.mlsender.net", "Frayed Studio") # Update to your domain
                .to_many([{"email": subscriber.email, "name": "Subscriber"}])
                .subject(newsletter.subject)
                .html(newsletter.html_content) # <--- Fixed field name!
                .text(plain_text_content)      # <--- Clean plain text fallback!
                .build()
            )
            
            # Send it!
            ms.emails.send(email)
            success_count += 1
            
            # Pause to ensure we stay under the API limit
            time.sleep(0.5) 
            
        # 5. Mark the newsletter as sent in the database!
        newsletter.was_sent = True
        newsletter.save()
            
        return f"Successfully sent to {success_count} subscribers."
        
    except Exception as e:
        return f"Failed to send: {str(e)}"