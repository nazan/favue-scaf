"""
Transactional email service.

Transport: pluggable ``EmailTransport`` implementations. The scaffold ships with
``LogEmailTransport`` only — it logs the message (developer / local use). Add
other transports (SMTP, HTTP API, etc.) by subclassing ``EmailTransport`` and
registering the implementation in ``service_init``.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import List, Optional

from app.config import settings


class EmailTransport(ABC):
    """Abstract base class for email transport."""

    @abstractmethod
    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        """Send an email. Return True if accepted for delivery (or logged)."""


class LogEmailTransport(EmailTransport):
    """Development transport: writes the message to the application log."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    async def send_email(
        self,
        to: str | List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
    ) -> bool:
        recipients = to if isinstance(to, list) else [to]
        self.logger.info("=" * 80)
        self.logger.info("EMAIL (log transport)")
        self.logger.info("From: %s (%s)", settings.email_from_address, settings.email_from_name)
        self.logger.info("To: %s", ", ".join(recipients))
        self.logger.info("Subject: %s", subject)
        self.logger.info("-" * 80)
        self.logger.info("Body:\n%s", body)
        if html_body:
            self.logger.info("-" * 80)
            self.logger.info("HTML Body:\n%s", html_body)
        self.logger.info("=" * 80)
        return True


class EmailService:
    """Transactional email facade using a transport adapter."""

    def __init__(
        self,
        transport: EmailTransport,
        logger: Optional[logging.Logger] = None,
    ):
        self.transport = transport
        self.logger = logger or logging.getLogger(__name__)

    async def send_verification_email(self, to: str, verification_token: str) -> bool:
        """Send identity / email verification link (transactional)."""
        base = settings.email_verify_base_url.rstrip("/")
        verification_url = f"{base}/verify-email?token={verification_token}"
        project = settings.project_name
        subject = f"Verify your {project} account"
        body = f"""
Hello,

Thank you for registering with {project}.

Please verify your email by opening this link in your browser:

{verification_url}

If you did not create an account, you can ignore this email.

Best regards,
{settings.email_from_name}
"""
        html_body = f"""
<html>
<body>
<h2>Verify your {project} account</h2>
<p>Thank you for registering with {project}.</p>
<p>Please verify your email by clicking the link below:</p>
<p><a href="{verification_url}">{verification_url}</a></p>
<p>If you did not create an account, you can ignore this email.</p>
<p>Best regards,<br>{settings.email_from_name}</p>
</body>
</html>
"""
        return await self.transport.send_email(
            to=to,
            subject=subject,
            body=body.strip(),
            html_body=html_body,
        )
