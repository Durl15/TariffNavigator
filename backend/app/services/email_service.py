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

    async def send_subscription_created_email(
        self,
        to_email: str,
        user_name: str,
        plan: str,
        organization_name: str,
        next_billing_date: str,
        calculations_limit: int
    ) -> bool:
        """
        Send welcome email when subscription is created.

        Args:
            to_email: User email
            user_name: User's full name
            plan: Subscription plan ('pro' or 'enterprise')
            organization_name: Organization name
            next_billing_date: Next billing date string
            calculations_limit: Monthly calculation limit

        Returns:
            bool: True if sent successfully
        """
        try:
            # Plan details
            price = "49" if plan == "pro" else "199"
            plan_name = plan.capitalize()

            html_body = self.render_template('subscription_created.html', {
                'user_name': user_name,
                'plan': plan,
                'plan_name': plan_name,
                'price': price,
                'next_billing_date': next_billing_date,
                'calculations_limit': f"{calculations_limit:,}",
                'dashboard_url': f"{settings.FRONTEND_URL}/dashboard",
                'help_url': f"{settings.FRONTEND_URL}/help",
                'billing_url': f"{settings.FRONTEND_URL}/billing",
                'unsubscribe_url': f"{settings.FRONTEND_URL}/settings/notifications"
            })

            subject = f"Welcome to TariffNavigator {plan_name}! 🎉"
            return await self.send_email(to_email, subject, html_body)

        except Exception as e:
            logger.error(f"Failed to send subscription created email: {str(e)}")
            return False

    async def send_payment_failed_email(
        self,
        to_email: str,
        user_name: str,
        plan: str,
        amount: float,
        attempt_count: int,
        billing_date: str
    ) -> bool:
        """
        Send email when payment fails.

        Args:
            to_email: User email
            user_name: User's full name
            plan: Subscription plan
            amount: Amount due
            attempt_count: Number of payment attempts
            billing_date: Billing date string

        Returns:
            bool: True if sent successfully
        """
        try:
            plan_name = plan.capitalize()

            html_body = self.render_template('payment_failed.html', {
                'user_name': user_name,
                'plan_name': plan_name,
                'amount': f"{amount:.2f}",
                'attempt_count': attempt_count,
                'billing_date': billing_date,
                'update_payment_url': f"{settings.FRONTEND_URL}/billing"
            })

            subject = "⚠️ Payment Failed - Action Required"
            return await self.send_email(to_email, subject, html_body)

        except Exception as e:
            logger.error(f"Failed to send payment failed email: {str(e)}")
            return False

    async def send_subscription_canceled_email(
        self,
        to_email: str,
        user_name: str,
        plan: str,
        access_until: str
    ) -> bool:
        """
        Send confirmation email when subscription is canceled.

        Args:
            to_email: User email
            user_name: User's full name
            plan: Subscription plan that was canceled
            access_until: Date when access ends

        Returns:
            bool: True if sent successfully
        """
        try:
            plan_name = plan.capitalize()

            html_body = self.render_template('subscription_canceled.html', {
                'user_name': user_name,
                'plan_name': plan_name,
                'access_until': access_until,
                'reactivate_url': f"{settings.FRONTEND_URL}/pricing"
            })

            subject = "Subscription Canceled - We're sorry to see you go"
            return await self.send_email(to_email, subject, html_body)

        except Exception as e:
            logger.error(f"Failed to send subscription canceled email: {str(e)}")
            return False

    async def send_quota_warning_email(
        self,
        to_email: str,
        user_name: str,
        plan: str,
        quota_type: str,
        current_usage: int,
        quota_limit: int,
        usage_percentage: float,
        reset_date: str,
        days_until_reset: int
    ) -> bool:
        """
        Send warning email when approaching quota limit (80%).

        Args:
            to_email: User email
            user_name: User's full name
            plan: Current plan
            quota_type: Type of quota ('calculations', 'watchlists', etc.)
            current_usage: Current usage count
            quota_limit: Quota limit
            usage_percentage: Percentage used
            reset_date: When quota resets
            days_until_reset: Days until reset

        Returns:
            bool: True if sent successfully
        """
        try:
            plan_name = plan.capitalize()

            # Format quota type for display
            quota_display = quota_type.replace('_', ' ').title()

            # Define action blocked
            action_map = {
                'calculations': 'perform calculations',
                'watchlists': 'create watchlists',
                'saved_calculations': 'save calculations'
            }
            action_blocked = action_map.get(quota_type, quota_type)

            # Higher plan limits
            pro_limit = "1,000" if quota_type == 'calculations' else "10"
            enterprise_limit = "10,000" if quota_type == 'calculations' else "Unlimited"

            html_body = self.render_template('quota_warning.html', {
                'user_name': user_name,
                'plan': plan,
                'plan_name': plan_name,
                'quota_type': quota_display,
                'current_usage': f"{current_usage:,}",
                'quota_limit': f"{quota_limit:,}",
                'usage_percentage': f"{usage_percentage:.0f}",
                'reset_date': reset_date,
                'days_until_reset': days_until_reset,
                'action_blocked': action_blocked,
                'pro_limit': pro_limit,
                'enterprise_limit': enterprise_limit,
                'upgrade_url': f"{settings.FRONTEND_URL}/pricing",
                'billing_url': f"{settings.FRONTEND_URL}/billing"
            })

            subject = f"⚠️ Approaching Your {quota_display} Limit"
            return await self.send_email(to_email, subject, html_body)

        except Exception as e:
            logger.error(f"Failed to send quota warning email: {str(e)}")
            return False

    async def send_quota_exceeded_email(
        self,
        to_email: str,
        user_name: str,
        plan: str,
        quota_type: str,
        current_usage: int,
        quota_limit: int,
        reset_date: str,
        days_until_reset: int
    ) -> bool:
        """
        Send alert email when quota limit is exceeded.

        Args:
            to_email: User email
            user_name: User's full name
            plan: Current plan
            quota_type: Type of quota
            current_usage: Current usage count
            quota_limit: Quota limit
            reset_date: When quota resets
            days_until_reset: Days until reset

        Returns:
            bool: True if sent successfully
        """
        try:
            plan_name = plan.capitalize()
            quota_display = quota_type.replace('_', ' ').title()

            action_map = {
                'calculations': 'perform calculations',
                'watchlists': 'create watchlists',
                'saved_calculations': 'save calculations'
            }
            action_blocked = action_map.get(quota_type, quota_type)

            pro_limit = "1,000" if quota_type == 'calculations' else "10"
            enterprise_limit = "10,000" if quota_type == 'calculations' else "Unlimited"

            html_body = self.render_template('quota_exceeded.html', {
                'user_name': user_name,
                'plan': plan,
                'plan_name': plan_name,
                'quota_type': quota_display,
                'current_usage': f"{current_usage:,}",
                'quota_limit': f"{quota_limit:,}",
                'reset_date': reset_date,
                'days_until_reset': days_until_reset,
                'action_blocked': action_blocked,
                'pro_limit': pro_limit,
                'enterprise_limit': enterprise_limit,
                'upgrade_url': f"{settings.FRONTEND_URL}/pricing",
                'billing_url': f"{settings.FRONTEND_URL}/billing"
            })

            subject = f"❌ {quota_display} Limit Reached"
            return await self.send_email(to_email, subject, html_body)

        except Exception as e:
            logger.error(f"Failed to send quota exceeded email: {str(e)}")
            return False


# Global instance
email_service = EmailService()
