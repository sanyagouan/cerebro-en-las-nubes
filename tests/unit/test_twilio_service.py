"""
Unit tests for TwilioService.
Tests the WhatsApp messaging functionality with mocked Twilio client.
"""

import pytest
from unittest.mock import MagicMock, patch, Mock
import os
from src.infrastructure.external.twilio_service import TwilioService


class TestTwilioServiceInit:
    """Tests for TwilioService initialization"""

    @patch.dict(
        os.environ,
        {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
        },
    )
    @patch("src.infrastructure.external.twilio_service.Client")
    def test_init_with_credentials(self, mock_client):
        """Test initialization with valid credentials"""
        service = TwilioService()

        assert service.sid == "test_sid"
        assert service.token == "test_token"
        assert service.whatsapp_from == "whatsapp:+14155238886"
        mock_client.assert_called_once_with("test_sid", "test_token")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_credentials(self):
        """Test initialization without credentials (mock mode)"""
        service = TwilioService()

        assert service.client is None
        assert service.sid is None
        assert service.token is None


class TestTwilioServiceSendWhatsApp:
    """Tests for send_whatsapp method"""

    @patch.dict(
        os.environ,
        {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
        },
    )
    @patch("src.infrastructure.external.twilio_service.Client")
    def test_send_whatsapp_success(self, mock_client):
        """Test successful WhatsApp message sending"""
        # Setup mock
        mock_message = Mock()
        mock_message.sid = "SM1234567890abcdef"
        mock_client.return_value.messages.create.return_value = mock_message

        service = TwilioService()
        result = service.send_whatsapp("+34600123456", "Test message")

        assert result == "SM1234567890abcdef"
        mock_client.return_value.messages.create.assert_called_once_with(
            body="Test message",
            from_="whatsapp:+14155238886",
            to="whatsapp:+34600123456",
        )

    @patch.dict(
        os.environ,
        {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_WHATSAPP_FROM": "+14155238886",  # Without whatsapp: prefix
        },
    )
    @patch("src.infrastructure.external.twilio_service.Client")
    def test_send_whatsapp_uses_from_as_configured(self, mock_client):
        """Test that from number is used as configured in environment (prefix handling is config responsibility)"""
        mock_message = Mock()
        mock_message.sid = "SM1234567890abcdef"
        mock_client.return_value.messages.create.return_value = mock_message

        service = TwilioService()
        result = service.send_whatsapp("+34600123456", "Test message")

        # Note: The implementation uses TWILIO_WHATSAPP_FROM as-is.
        # It's the responsibility of the environment configuration to include the whatsapp: prefix.
        # This test verifies the current behavior - the from number is used exactly as configured.
        mock_client.return_value.messages.create.assert_called_once_with(
            body="Test message",
            from_="+14155238886",  # Used as configured (without prefix in this test case)
            to="whatsapp:+34600123456",
        )

    @patch.dict(
        os.environ,
        {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
        },
    )
    @patch("src.infrastructure.external.twilio_service.Client")
    def test_send_whatsapp_handles_prefixed_number(self, mock_client):
        """Test that already prefixed numbers are handled correctly"""
        mock_message = Mock()
        mock_message.sid = "SM1234567890abcdef"
        mock_client.return_value.messages.create.return_value = mock_message

        service = TwilioService()
        result = service.send_whatsapp("whatsapp:+34600123456", "Test message")

        mock_client.return_value.messages.create.assert_called_once_with(
            body="Test message",
            from_="whatsapp:+14155238886",
            to="whatsapp:+34600123456",  # Should not double-prefix
        )

    @patch.dict(os.environ, {}, clear=True)
    def test_send_whatsapp_mock_mode(self):
        """Test mock mode when credentials are not available - returns None when client not initialized"""
        service = TwilioService()
        result = service.send_whatsapp("+34600123456", "Test message")

        assert result is None

    @patch.dict(
        os.environ,
        {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
        },
    )
    @patch("src.infrastructure.external.twilio_service.Client")
    def test_send_whatsapp_handles_exception(self, mock_client):
        """Test error handling when Twilio raises an exception"""
        mock_client.return_value.messages.create.side_effect = Exception("Twilio error")

        service = TwilioService()
        result = service.send_whatsapp("+34600123456", "Test message")

        assert result is None


class TestTwilioServiceSendSMS:
    """Tests for deprecated send_sms method"""

    @patch.dict(os.environ, {}, clear=True)
    def test_send_sms_calls_send_whatsapp(self):
        """Test that send_sms calls send_whatsapp internally"""
        service = TwilioService()

        with patch.object(
            service, "send_whatsapp", return_value="MOCK_SID"
        ) as mock_whatsapp:
            result = service.send_sms("+34600123456", "Test message")

            mock_whatsapp.assert_called_once_with("+34600123456", "Test message")
            assert result == "MOCK_SID"


# Edge case tests
class TestTwilioServiceEdgeCases:
    """Tests for edge cases and error conditions"""

    @patch.dict(
        os.environ,
        {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
        },
    )
    @patch("src.infrastructure.external.twilio_service.Client")
    def test_send_whatsapp_empty_message(self, mock_client):
        """Test sending empty message"""
        mock_message = Mock()
        mock_message.sid = "SM1234567890abcdef"
        mock_client.return_value.messages.create.return_value = mock_message

        service = TwilioService()
        result = service.send_whatsapp("+34600123456", "")

        assert result == "SM1234567890abcdef"

    @patch.dict(
        os.environ,
        {
            "TWILIO_ACCOUNT_SID": "test_sid",
            "TWILIO_AUTH_TOKEN": "test_token",
            "TWILIO_WHATSAPP_FROM": "whatsapp:+14155238886",
        },
    )
    @patch("src.infrastructure.external.twilio_service.Client")
    def test_send_whatsapp_long_message(self, mock_client):
        """Test sending long message (1600+ chars for WhatsApp limit)"""
        mock_message = Mock()
        mock_message.sid = "SM1234567890abcdef"
        mock_client.return_value.messages.create.return_value = mock_message

        service = TwilioService()
        long_message = "A" * 2000  # 2000 characters
        result = service.send_whatsapp("+34600123456", long_message)

        assert result == "SM1234567890abcdef"
        # Verify the full message was passed (Twilio handles segmentation)
        call_args = mock_client.return_value.messages.create.call_args
        assert len(call_args[1]["body"]) == 2000
