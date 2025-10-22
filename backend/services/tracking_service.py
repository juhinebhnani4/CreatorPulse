"""
Tracking Service - Generate tracking pixels and tracked links for email analytics.

This service handles:
- Generating tracking pixel URLs
- Adding UTM parameters to links
- Adding click tracking to links
- Inserting tracking code into email HTML
"""

import base64
import json
import re
from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from uuid import UUID

from bs4 import BeautifulSoup

from backend.settings import settings


class TrackingService:
    """Service for generating email tracking code."""

    def __init__(self):
        self.tracking_domain = settings.backend_url

    def generate_tracking_pixel_url(
        self, newsletter_id: UUID, recipient_email: str, workspace_id: UUID
    ) -> str:
        """
        Generate tracking pixel URL for email open tracking.

        Args:
            newsletter_id: Newsletter UUID
            recipient_email: Recipient email address
            workspace_id: Workspace UUID

        Returns:
            URL to 1×1 transparent PNG tracking pixel
        """
        params = {
            "n": str(newsletter_id),
            "r": recipient_email,
            "w": str(workspace_id),
        }

        # Encode parameters
        encoded = base64.urlsafe_b64encode(json.dumps(params).encode()).decode()

        # Generate URL
        return f"{self.tracking_domain}/track/pixel/{encoded}.png"

    def generate_tracked_link(
        self,
        original_url: str,
        newsletter_id: UUID,
        recipient_email: str,
        workspace_id: UUID,
        content_item_id: Optional[UUID] = None,
    ) -> str:
        """
        Generate tracked link with UTM parameters and redirect tracking.

        Args:
            original_url: Original URL to track
            newsletter_id: Newsletter UUID
            recipient_email: Recipient email address
            workspace_id: Workspace UUID
            content_item_id: Content item UUID (optional)

        Returns:
            Tracked URL with UTM parameters
        """
        # Skip tracking for special URLs
        if original_url.startswith(("mailto:", "tel:", "sms:", "#")):
            return original_url

        parsed = urlparse(original_url)
        params = parse_qs(parsed.query)

        # Add UTM parameters
        params.update({
            "utm_source": ["newsletter"],
            "utm_medium": ["email"],
            "utm_campaign": [str(newsletter_id)[:8]],  # Shortened for readability
        })

        if content_item_id:
            params["utm_content"] = [str(content_item_id)[:8]]

        # Rebuild URL with UTM parameters
        new_query = urlencode(params, doseq=True)
        tracked_url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment,
        ))

        # Option 1: Direct URL with UTM (simpler, no redirect)
        # Return tracked_url directly if you don't need server-side click tracking

        # Option 2: Add redirect tracking (for server-side click recording)
        # Encode tracking data
        track_data = {
            "n": str(newsletter_id),
            "r": recipient_email,
            "w": str(workspace_id),
            "c": str(content_item_id) if content_item_id else None,
            "u": tracked_url,  # Original URL with UTM
        }

        encoded_track = base64.urlsafe_b64encode(json.dumps(track_data).encode()).decode()

        # Return redirect URL
        return f"{self.tracking_domain}/track/click/{encoded_track}"

    def add_tracking_to_html(
        self,
        html_content: str,
        newsletter_id: UUID,
        recipient_email: str,
        workspace_id: UUID,
        content_items: Optional[List[Dict]] = None,
    ) -> str:
        """
        Add tracking pixel and link tracking to email HTML.

        Args:
            html_content: Original HTML content
            newsletter_id: Newsletter UUID
            recipient_email: Recipient email address
            workspace_id: Workspace UUID
            content_items: List of content items with IDs (optional)

        Returns:
            HTML with tracking pixel and tracked links
        """
        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # 1. Add tracking pixel at the end of body
        pixel_url = self.generate_tracking_pixel_url(
            newsletter_id, recipient_email, workspace_id
        )

        # Create tracking pixel element
        pixel_img = soup.new_tag(
            "img",
            src=pixel_url,
            width="1",
            height="1",
            alt="",
            style="display:none;",
        )

        # Insert before closing body tag or at end
        body = soup.find("body")
        if body:
            body.append(pixel_img)
        else:
            # If no body tag, append to end
            soup.append(pixel_img)

        # 2. Add tracking to all links
        content_item_map = {}
        if content_items:
            # Map URLs to content item IDs for tracking
            for item in content_items:
                if "source_url" in item and "id" in item:
                    content_item_map[item["source_url"]] = item["id"]

        for link in soup.find_all("a", href=True):
            original_url = link["href"]

            # Skip special URLs
            if original_url.startswith(("mailto:", "tel:", "sms:", "#")):
                continue

            # Find matching content item ID
            content_item_id = content_item_map.get(original_url)

            # Generate tracked URL
            tracked_url = self.generate_tracked_link(
                original_url,
                newsletter_id,
                recipient_email,
                workspace_id,
                content_item_id,
            )

            # Update link
            link["href"] = tracked_url

        # 3. Return modified HTML
        return str(soup)

    def add_unsubscribe_link(
        self, html_content: str, workspace_id: UUID, recipient_email: str
    ) -> str:
        """
        Add unsubscribe link to email HTML (required for CAN-SPAM compliance).

        Args:
            html_content: Original HTML content
            workspace_id: Workspace UUID
            recipient_email: Recipient email address

        Returns:
            HTML with unsubscribe link added
        """
        # Generate unsubscribe URL
        params = {
            "w": str(workspace_id),
            "e": recipient_email,
        }
        encoded = base64.urlsafe_b64encode(json.dumps(params).encode()).decode()
        unsubscribe_url = f"{self.tracking_domain}/unsubscribe/{encoded}"

        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Find footer or create one
        footer = soup.find("footer")
        if not footer:
            footer = soup.new_tag("footer", style="text-align:center; padding:20px; color:#666; font-size:12px;")
            body = soup.find("body")
            if body:
                body.append(footer)
            else:
                soup.append(footer)

        # Add unsubscribe link
        unsubscribe_text = soup.new_tag("p")
        unsubscribe_link = soup.new_tag("a", href=unsubscribe_url, style="color:#666; text-decoration:underline;")
        unsubscribe_link.string = "Unsubscribe"

        unsubscribe_text.append("Don't want to receive these emails? ")
        unsubscribe_text.append(unsubscribe_link)

        footer.append(unsubscribe_text)

        return str(soup)

    def decode_tracking_params(self, encoded_params: str) -> Dict:
        """
        Decode tracking parameters from encoded string.

        Args:
            encoded_params: Base64-encoded JSON string

        Returns:
            Decoded parameters dict
        """
        try:
            decoded = base64.urlsafe_b64decode(encoded_params.encode()).decode()
            params = json.loads(decoded)
            return params
        except Exception as e:
            raise ValueError(f"Invalid tracking parameters: {e}")

    def extract_utm_parameters(self, url: str) -> Dict[str, str]:
        """
        Extract UTM parameters from URL.

        Args:
            url: URL with UTM parameters

        Returns:
            Dict of UTM parameters
        """
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        utm_params = {}
        for key in ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"]:
            if key in params:
                utm_params[key] = params[key][0]  # Get first value

        return utm_params

    def generate_preview_text(self, html_content: str, max_length: int = 150) -> str:
        """
        Generate preview text from HTML content (shown in email clients).

        Args:
            html_content: HTML content
            max_length: Maximum length of preview text

        Returns:
            Plain text preview
        """
        # Parse HTML
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Get text
        text = soup.get_text()

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = " ".join(chunk for chunk in chunks if chunk)

        # Truncate
        if len(text) > max_length:
            text = text[:max_length] + "..."

        return text

    def add_list_unsubscribe_header(self, workspace_id: UUID, recipient_email: str) -> Dict[str, str]:
        """
        Generate List-Unsubscribe header for email (improves deliverability).

        Args:
            workspace_id: Workspace UUID
            recipient_email: Recipient email address

        Returns:
            Dict with email headers
        """
        # Generate unsubscribe URL
        params = {"w": str(workspace_id), "e": recipient_email}
        encoded = base64.urlsafe_b64encode(json.dumps(params).encode()).decode()
        unsubscribe_url = f"{self.tracking_domain}/unsubscribe/{encoded}"

        return {
            "List-Unsubscribe": f"<{unsubscribe_url}>",
            "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        }
