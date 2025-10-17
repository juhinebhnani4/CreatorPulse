"""
Email delivery system using SMTP or SendGrid.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
import re
from datetime import datetime

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
except ImportError:
    SendGridAPIClient = None
    Mail = None

from ..config.settings import EmailConfig


class EmailSender:
    """
    Email delivery system supporting both SMTP and SendGrid.
    
    Example:
        sender = EmailSender(config=email_config)
        success = sender.send_newsletter("user@example.com", "Newsletter Title", html_content)
    """
    
    def __init__(self, config: Optional[EmailConfig] = None):
        """
        Initialize the email sender.
        
        Args:
            config: Email configuration
        """
        self.config = config or EmailConfig()
        self.logger = self._setup_logger()
        
        # Initialize SendGrid client if configured
        self.sendgrid_client = None
        if self.config.use_sendgrid and self.config.sendgrid_api_key:
            if not SendGridAPIClient:
                raise ImportError("SendGrid package is required. Install with: pip install sendgrid")
            
            try:
                self.sendgrid_client = SendGridAPIClient(api_key=self.config.sendgrid_api_key)
                self.logger.info("SendGrid client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize SendGrid client: {e}")
                raise
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logger for the email sender."""
        logger = logging.getLogger(f"{self.__class__.__name__}")
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def send_newsletter(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> bool:
        """
        Send a newsletter email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the newsletter
            text_content: Plain text content (optional)
            from_email: Sender email (if not provided, uses config)
            from_name: Sender name (if not provided, uses config)
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.validate_email(to_email):
            self.logger.error(f"Invalid email address: {to_email}")
            return False
        
        from_email = from_email or self.config.from_email
        from_name = from_name or self.config.from_name
        
        if not from_email:
            self.logger.error("No sender email configured")
            return False
        
        try:
            if self.config.use_sendgrid and self.sendgrid_client:
                return self._send_via_sendgrid(
                    to_email, subject, html_content, text_content, from_email, from_name
                )
            else:
                return self._send_via_smtp(
                    to_email, subject, html_content, text_content, from_email, from_name
                )
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
            return False
    
    def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: str,
        from_name: str
    ) -> bool:
        """Send email via SendGrid."""
        try:
            from_email_obj = Email(from_email, from_name)
            to_email_obj = To(to_email)
            
            if text_content:
                content = Content("text/html", html_content)
                text_content_obj = Content("text/plain", text_content)
            else:
                content = Content("text/html", html_content)
                text_content_obj = None
            
            mail = Mail(from_email_obj, to_email_obj, subject, content)
            
            if text_content_obj:
                mail.add_content(text_content_obj)
            
            response = self.sendgrid_client.send(mail)
            
            if response.status_code in [200, 201, 202]:
                self.logger.info(f"Email sent successfully via SendGrid to {to_email}")
                return True
            else:
                self.logger.error(f"SendGrid error: {response.status_code} - {response.body}")
                return False
                
        except Exception as e:
            self.logger.error(f"SendGrid API error: {e}")
            return False
    
    def _send_via_smtp(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str],
        from_email: str,
        from_name: str
    ) -> bool:
        """Send email via SMTP."""
        if not self.config.smtp_server:
            self.logger.error("SMTP server not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name} <{from_email}>"
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Connect to SMTP server
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls(context=context)
                
                if self.config.smtp_username and self.config.smtp_password:
                    server.login(self.config.smtp_username, self.config.smtp_password)
                
                # Send email
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully via SMTP to {to_email}")
            return True
            
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"SMTP connection error: {e}")
            return False
    
    def send_bulk_newsletter(
        self,
        recipients: List[str],
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send newsletter to multiple recipients.
        
        Args:
            recipients: List of recipient email addresses
            subject: Email subject
            html_content: HTML content of the newsletter
            text_content: Plain text content (optional)
            from_email: Sender email (if not provided, uses config)
            from_name: Sender name (if not provided, uses config)
            
        Returns:
            Dictionary with results: {'sent': int, 'failed': int, 'errors': List[str]}
        """
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        if not recipients:
            results['errors'].append("No recipients provided")
            return results
        
        # Validate all emails first
        valid_recipients = []
        for email in recipients:
            if self.validate_email(email):
                valid_recipients.append(email)
            else:
                results['failed'] += 1
                results['errors'].append(f"Invalid email address: {email}")
        
        if not valid_recipients:
            results['errors'].append("No valid email addresses found")
            return results
        
        # Send to each valid recipient
        for email in valid_recipients:
            try:
                success = self.send_newsletter(
                    email, subject, html_content, text_content, from_email, from_name
                )
                
                if success:
                    results['sent'] += 1
                    self.logger.info(f"Newsletter sent successfully to {email}")
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to send to {email}")
                    
            except Exception as e:
                results['failed'] += 1
                error_msg = f"Error sending to {email}: {str(e)}"
                results['errors'].append(error_msg)
                self.logger.error(error_msg)
        
        self.logger.info(f"Bulk send completed: {results['sent']} sent, {results['failed']} failed")
        return results
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def test_connection(self) -> bool:
        """
        Test email connection configuration.
        
        Returns:
            True if connection successful, False otherwise
        """
        if self.config.use_sendgrid and self.sendgrid_client:
            return self._test_sendgrid_connection()
        else:
            return self._test_smtp_connection()
    
    def _test_sendgrid_connection(self) -> bool:
        """Test SendGrid connection."""
        try:
            # Try to get account info (this is a lightweight API call)
            response = self.sendgrid_client.client.user.account.get()
            if response.status_code == 200:
                self.logger.info("SendGrid connection test successful")
                return True
            else:
                self.logger.error(f"SendGrid connection test failed: {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"SendGrid connection test error: {e}")
            return False
    
    def _test_smtp_connection(self) -> bool:
        """Test SMTP connection."""
        if not self.config.smtp_server:
            self.logger.error("SMTP server not configured")
            return False
        
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls(context=context)
                
                if self.config.smtp_username and self.config.smtp_password:
                    server.login(self.config.smtp_username, self.config.smtp_password)
            
            self.logger.info("SMTP connection test successful")
            return True
            
        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP connection test failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"SMTP connection test error: {e}")
            return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """
        Get email configuration status.
        
        Returns:
            Dictionary with configuration status
        """
        status = {
            'provider': 'SendGrid' if self.config.use_sendgrid else 'SMTP',
            'configured': False,
            'connection_test': False,
            'missing_config': []
        }
        
        if self.config.use_sendgrid:
            if self.config.sendgrid_api_key:
                status['configured'] = True
            else:
                status['missing_config'].append('sendgrid_api_key')
        else:
            required_fields = ['smtp_server', 'smtp_port', 'from_email']
            missing = [field for field in required_fields if not getattr(self.config, field)]
            
            if not missing:
                status['configured'] = True
            else:
                status['missing_config'] = missing
        
        # Test connection if configured
        if status['configured']:
            status['connection_test'] = self.test_connection()
        
        return status
