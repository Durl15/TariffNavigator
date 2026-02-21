"""
Email Service for sending notification emails and digests.
"""
import logging
from typing import List, Optional
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path

from app.core.config import settings
from app.models.notification import Notification

logger = logging.getLogger(__name__)

# Setup Jinja2 for email templates
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "emails"
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(['html', 'xml'])
)


class EmailService:
    """Service for sending emails via SMTP."""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email via SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (fallback)

        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.from_name} <{self.from_email}>"
            message['To'] = to_email

            # Attach text and HTML parts
            if text_body:
                text_part = MIMEText(text_body, 'plain')
                message.attach(text_part)

            html_part = MIMEText(html_body, 'html')
            message.attach(html_part)

            # Send email
            # For Mailtrap port 2525, TLS is optional
            use_tls = self.smtp_port in [587, 465]

            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=use_tls if self.smtp_port != 465 else False,
                use_tls=True if self.smtp_port == 465 else False
            )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def render_template(self, template_name: str, context: dict) -> str:
        """
        Render an email template with context.

        Args:
            template_name: Name of template file (e.g., 'notification.html')
            context: Template context variables

        Returns:
            str: Rendered HTML
        """
        try:
            template = jinja_env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Failed to render template {template_name}: {str(e)}")
            raise

    async def send_notification_email(
        self,
        to_email: str,
        notification: Notification
    ) -> bool:
        """
        Send a single notification via email.

        Args:
            to_email: Recipient email
            notification: Notification object

        Returns:
            bool: True if sent successfully
        """
        try:
            # Render email template
            html_body = self.render_template('notification.html', {
                'notification': notification,
                'title': notification.title,
                'message': notification.message,
                'link': notification.link,
                'created_at': notification.created_at,
                'app_name': 'TariffNavigator',
                'app_url': settings.FRONTEND_URL
            })

            # Send email
            subject = f"TariffNavigator: {notification.title}"
            return await self.send_email(to_email, subject, html_body)

        except Exception as e:
            logger.error(f"Failed to send notification email: {str(e)}")
            return False

    async def send_digest_email(
        self,
        to_email: str,
        notifications: List[Notification],
        frequency: str = 'daily'
    ) -> bool:
        """
        Send a digest email with multiple notifications.

        Args:
            to_email: Recipient email
            notifications: List of notifications
            frequency: 'daily' or 'weekly'

        Returns:
            bool: True if sent successfully
        """
        try:
            # Choose template based on frequency
            template_name = f"{frequency}_digest.html"

            # Render email template
            html_body = self.render_template(template_name, {
                'notifications': notifications,
                'notification_count': len(notifications),
                'frequency': frequency,
                'date': datetime.now().strftime('%B %d, %Y'),
                'app_name': 'TariffNavigator',
                'app_url': settings.FRONTEND_URL,
                'unsubscribe_url': f"{settings.FRONTEND_URL}/settings/notifications"
            })

            # Send email
            subject = f"TariffNavigator {frequency.capitalize()} Digest - {len(notifications)} Updates"
            return await self.send_email(to_email, subject, html_body)

        except Exception as e:
            logger.error(f"Failed to send digest email: {str(e)}")
            return False


# Global instance
email_service = EmailService()
