"""
Unit tests for email sender.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import smtplib

from ai_newsletter.delivery.email_sender import EmailSender


class TestEmailSender:
    """Test cases for EmailSender."""
    
    def test_init_with_smtp_config(self):
        """Test EmailSender initialization with SMTP config."""
        config = Mock()
        config.use_sendgrid = False
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.smtp_username = "test@example.com"
        config.smtp_password = "test_password"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        config.use_tls = True
        
        sender = EmailSender(config=config)
        
        assert sender.config == config
        assert sender.config.use_sendgrid == False
    
    def test_init_with_sendgrid_config(self):
        """Test EmailSender initialization with SendGrid config."""
        config = Mock()
        config.use_sendgrid = True
        config.sendgrid_api_key = "test_api_key"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        
        sender = EmailSender(config=config)
        
        assert sender.config == config
        assert sender.config.use_sendgrid == True
    
    def test_init_without_config(self):
        """Test EmailSender initialization without config."""
        with patch('ai_newsletter.delivery.email_sender.get_settings') as mock_settings:
            mock_settings.return_value.email = Mock()
            mock_settings.return_value.email.use_sendgrid = False
            mock_settings.return_value.email.smtp_server = "smtp.gmail.com"
            mock_settings.return_value.email.smtp_port = 587
            mock_settings.return_value.email.smtp_username = "test@example.com"
            mock_settings.return_value.email.smtp_password = "test_password"
            mock_settings.return_value.email.from_email = "test@example.com"
            mock_settings.return_value.email.from_name = "Test Sender"
            mock_settings.return_value.email.use_tls = True
            
            sender = EmailSender()
            
            assert sender.config == mock_settings.return_value.email
    
    def test_validate_email_valid(self):
        """Test email validation with valid email."""
        config = Mock()
        config.use_sendgrid = False
        
        sender = EmailSender(config=config)
        
        assert sender.validate_email("test@example.com") == True
        assert sender.validate_email("user.name+tag@domain.co.uk") == True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid email."""
        config = Mock()
        config.use_sendgrid = False
        
        sender = EmailSender(config=config)
        
        assert sender.validate_email("invalid_email") == False
        assert sender.validate_email("@example.com") == False
        assert sender.validate_email("test@") == False
        assert sender.validate_email("") == False
        assert sender.validate_email(None) == False
    
    def test_send_smtp_email_success(self):
        """Test successful SMTP email sending."""
        config = Mock()
        config.use_sendgrid = False
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.smtp_username = "test@example.com"
        config.smtp_password = "test_password"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        config.use_tls = True
        
        sender = EmailSender(config=config)
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            result = sender._send_smtp_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test content</p>"
            )
            
            assert result == True
            mock_server.starttls.assert_called_once()
            mock_server.login.assert_called_once_with("test@example.com", "test_password")
            mock_server.sendmail.assert_called_once()
    
    def test_send_smtp_email_auth_error(self):
        """Test SMTP email sending with authentication error."""
        config = Mock()
        config.use_sendgrid = False
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.smtp_username = "test@example.com"
        config.smtp_password = "test_password"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        config.use_tls = True
        
        sender = EmailSender(config=config)
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            mock_server.login.side_effect = smtplib.SMTPAuthenticationError("Auth failed")
            
            result = sender._send_smtp_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test content</p>"
            )
            
            assert result == False
    
    def test_send_smtp_email_connection_error(self):
        """Test SMTP email sending with connection error."""
        config = Mock()
        config.use_sendgrid = False
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.smtp_username = "test@example.com"
        config.smtp_password = "test_password"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        config.use_tls = True
        
        sender = EmailSender(config=config)
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_smtp.side_effect = smtplib.SMTPConnectError("Connection failed")
            
            result = sender._send_smtp_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test content</p>"
            )
            
            assert result == False
    
    def test_send_sendgrid_email_success(self):
        """Test successful SendGrid email sending."""
        config = Mock()
        config.use_sendgrid = True
        config.sendgrid_api_key = "test_api_key"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        
        sender = EmailSender(config=config)
        
        with patch('ai_newsletter.delivery.email_sender.SendGridAPIClient') as mock_client:
            mock_sg = Mock()
            mock_client.return_value = mock_sg
            mock_response = Mock()
            mock_response.status_code = 202
            mock_sg.send.return_value = mock_response
            
            result = sender._send_sendgrid_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test content</p>"
            )
            
            assert result == True
            mock_sg.send.assert_called_once()
    
    def test_send_sendgrid_email_error(self):
        """Test SendGrid email sending with error."""
        config = Mock()
        config.use_sendgrid = True
        config.sendgrid_api_key = "test_api_key"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        
        sender = EmailSender(config=config)
        
        with patch('ai_newsletter.delivery.email_sender.SendGridAPIClient') as mock_client:
            mock_sg = Mock()
            mock_client.return_value = mock_sg
            mock_sg.send.side_effect = Exception("SendGrid error")
            
            result = sender._send_sendgrid_email(
                to_email="recipient@example.com",
                subject="Test Subject",
                html_content="<p>Test content</p>"
            )
            
            assert result == False
    
    def test_send_newsletter_smtp(self):
        """Test sending newsletter via SMTP."""
        config = Mock()
        config.use_sendgrid = False
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.smtp_username = "test@example.com"
        config.smtp_password = "test_password"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        config.use_tls = True
        
        sender = EmailSender(config=config)
        
        with patch.object(sender, '_send_smtp_email') as mock_send:
            mock_send.return_value = True
            
            result = sender.send_newsletter(
                to_email="recipient@example.com",
                subject="Test Newsletter",
                html_content="<p>Newsletter content</p>"
            )
            
            assert result == True
            mock_send.assert_called_once_with(
                "recipient@example.com",
                "Test Newsletter",
                "<p>Newsletter content</p>",
                None
            )
    
    def test_send_newsletter_sendgrid(self):
        """Test sending newsletter via SendGrid."""
        config = Mock()
        config.use_sendgrid = True
        config.sendgrid_api_key = "test_api_key"
        config.from_email = "test@example.com"
        config.from_name = "Test Sender"
        
        sender = EmailSender(config=config)
        
        with patch.object(sender, '_send_sendgrid_email') as mock_send:
            mock_send.return_value = True
            
            result = sender.send_newsletter(
                to_email="recipient@example.com",
                subject="Test Newsletter",
                html_content="<p>Newsletter content</p>"
            )
            
            assert result == True
            mock_send.assert_called_once_with(
                "recipient@example.com",
                "Test Newsletter",
                "<p>Newsletter content</p>",
                None
            )
    
    def test_send_newsletter_invalid_email(self):
        """Test sending newsletter with invalid email."""
        config = Mock()
        config.use_sendgrid = False
        
        sender = EmailSender(config=config)
        
        result = sender.send_newsletter(
            to_email="invalid_email",
            subject="Test Newsletter",
            html_content="<p>Newsletter content</p>"
        )
        
        assert result == False
    
    def test_get_config_status_smtp_configured(self):
        """Test getting config status for configured SMTP."""
        config = Mock()
        config.use_sendgrid = False
        config.smtp_server = "smtp.gmail.com"
        config.smtp_port = 587
        config.smtp_username = "test@example.com"
        config.smtp_password = "test_password"
        config.from_email = "test@example.com"
        config.use_tls = True
        
        sender = EmailSender(config=config)
        
        with patch('smtplib.SMTP') as mock_smtp:
            mock_server = Mock()
            mock_smtp.return_value.__enter__.return_value = mock_server
            
            status = sender.get_config_status()
            
            assert status['provider'] == 'SMTP'
            assert status['configured'] == True
            assert status['connection_test'] == True
            assert len(status['missing_config']) == 0
    
    def test_get_config_status_smtp_missing_config(self):
        """Test getting config status for SMTP with missing config."""
        config = Mock()
        config.use_sendgrid = False
        config.smtp_server = None
        config.smtp_port = 587
        config.smtp_username = None
        config.smtp_password = None
        config.from_email = None
        config.use_tls = True
        
        sender = EmailSender(config=config)
        
        status = sender.get_config_status()
        
        assert status['provider'] == 'SMTP'
        assert status['configured'] == False
        assert 'SMTP Server' in status['missing_config']
        assert 'SMTP Username' in status['missing_config']
        assert 'SMTP Password' in status['missing_config']
        assert 'From Email' in status['missing_config']
    
    def test_get_config_status_sendgrid_configured(self):
        """Test getting config status for configured SendGrid."""
        config = Mock()
        config.use_sendgrid = True
        config.sendgrid_api_key = "test_api_key"
        config.from_email = "test@example.com"
        
        sender = EmailSender(config=config)
        
        status = sender.get_config_status()
        
        assert status['provider'] == 'SendGrid'
        assert status['configured'] == True
        assert status['connection_test'] == True
        assert len(status['missing_config']) == 0
    
    def test_get_config_status_sendgrid_missing_config(self):
        """Test getting config status for SendGrid with missing config."""
        config = Mock()
        config.use_sendgrid = True
        config.sendgrid_api_key = None
        config.from_email = None
        
        sender = EmailSender(config=config)
        
        status = sender.get_config_status()
        
        assert status['provider'] == 'SendGrid'
        assert status['configured'] == False
        assert 'SendGrid API Key' in status['missing_config']
        assert 'From Email' in status['missing_config']