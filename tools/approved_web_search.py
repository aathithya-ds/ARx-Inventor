"""
ARX INVENTOR - Tool C: Approved Web Search & Safe Content Fetcher
Executes safe web queries via DuckDuckGo, enforces domain allowlists/denylists,
and fetches permitted page contents while guarding against SSRF and prompt injection.
"""

from typing import List, Dict, Any, Optional
import urllib.parse
import ipaddress
import socket
import re
import requests
from bs4 import BeautifulSoup
from config.settings import settings

class ApprovedWebSearchTool:
    """Performs web search and page fetching with security guardrails."""

    def __init__(
        self,
        allowed_domains: Optional[List[str]] = None,
        excluded_domains: Optional[List[str]] = None,
        timeout: int = settings.SEARCH_TIMEOUT,
        max_results: int = settings.MAX_SEARCH_RESULTS
    ):
        self.allowed_domains = [d.lower().strip() for d in (allowed_domains or []) if d.strip()]
        self.excluded_domains = [d.lower().strip() for d in (excluded_domains or settings.DEFAULT_EXCLUDED_DOMAINS) if d.strip()]
        self.timeout = timeout
        self.max_results = max_results

    def is_url_safe(self, url: str) -> tuple[bool, str]:
        """
        SSRF & Security Guardrail:
        Validates URL scheme, resolves hostname to IP, blocks loopback/private/internal addresses.
        """
        try:
            parsed = urllib.parse.urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False, f"Unsupported URL scheme: {parsed.scheme} (only HTTP/HTTPS allowed)"

            hostname = parsed.hostname
            if not hostname:
                return False, "Invalid URL: missing hostname"

            # Check domain allowlist
            if self.allowed_domains:
                domain_matches = any(
                    hostname == allowed or hostname.endswith("." + allowed)
                    for allowed in self.allowed_domains
                )
                if not domain_matches:
                    return False, f"Domain '{hostname}' is not in the allowed domains list: {self.allowed_domains}"

            # Check domain blocklist
            for excluded in self.excluded_domains:
                if hostname == excluded or hostname.endswith("." + excluded):
                    return False, f"Domain '{hostname}' matches excluded domain: {excluded}"

            # Resolve IP to protect against SSRF (private / loopback / link-local)
            try:
                ip_str = socket.gethostbyname(hostname)
                ip = ipaddress.ip_address(ip_str)
                if ip.is_loopback or ip.is_private or ip.is_link_local or ip.is_reserved:
                    return False, f"Access to private/local network address ({ip_str}) is prohibited"
            except socket.gaierror:
                return False, f"Unable to resolve host: {hostname}"

            return True, "URL is safe"
        except Exception as e:
            return False, f"URL validation failed: {str(e)}"

    def search(self, query: str) -> Dict[str, Any]:
        """
        Executes DuckDuckGo search and filters results by domain policy.
        """
        if not query.strip():
            return {"success": False, "query": query, "results": [], "error": "Query cannot be empty"}

        results = []
        try:
            from duckduckgo_search import DDGS
            with DDGS(timeout=self.timeout) as ddgs:
                raw_results = list(ddgs.text(query, max_results=self.max_results * 2))

            for r in raw_results:
                href = r.get("href") or r.get("link") or ""
                if not href:
                    continue

                safe, _ = self.is_url_safe(href)
                if safe:
                    results.append({
                        "title": r.get("title", "Untitled"),
                        "url": href,
                        "snippet": r.get("body") or r.get("snippet", ""),
                        "source_type": "web_search"
                    })
                if len(results) >= self.max_results:
                    break

            return {
                "success": True,
                "query": query,
                "total_found": len(results),
                "results": results,
                "error": None
            }
        except Exception as e:
            return {
                "success": False,
                "query": query,
                "total_found": 0,
                "results": [],
                "error": f"Web search provider error or timeout: {str(e)}"
            }

    def fetch_webpage_content(self, url: str) -> Dict[str, Any]:
        """
        Safely fetches and extracts readable text from an approved webpage.
        """
        safe, reason = self.is_url_safe(url)
        if not safe:
            return {
                "success": False,
                "url": url,
                "title": "",
                "text": "",
                "error": f"URL blocked by security guardrails: {reason}"
            }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ARX-ZENOVA-Research-Bot/1.0"
        }

        try:
            resp = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            if resp.status_code != 200:
                return {
                    "success": False,
                    "url": url,
                    "title": "",
                    "text": "",
                    "error": f"HTTP status code {resp.status_code} returned by web server"
                }

            # Check final URL after redirects for SSRF safety
            final_safe, final_reason = self.is_url_safe(resp.url)
            if not final_safe:
                return {
                    "success": False,
                    "url": resp.url,
                    "title": "",
                    "text": "",
                    "error": f"Redirected to unsafe URL: {final_reason}"
                }

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove scripts, styles, navigation, footer
            for el in soup(["script", "style", "nav", "footer", "header", "aside", "noscript"]):
                el.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else url
            text = soup.get_text(separator="\n", strip=True)

            # Guardrail: clean text against prompt injections
            cleaned_text = self._sanitize_web_text(text)

            # Limit text length to prevent huge context bloat (e.g. 15,000 chars)
            if len(cleaned_text) > 15000:
                cleaned_text = cleaned_text[:15000] + "\n...[Content truncated for length]..."

            return {
                "success": True,
                "url": resp.url,
                "title": title,
                "text": cleaned_text,
                "error": None
            }
        except requests.Timeout:
            return {
                "success": False,
                "url": url,
                "title": "",
                "text": "",
                "error": f"Connection timed out after {self.timeout} seconds"
            }
        except requests.RequestException as e:
            return {
                "success": False,
                "url": url,
                "title": "",
                "text": "",
                "error": f"Network error during web fetch: {str(e)}"
            }

    def _sanitize_web_text(self, text: str) -> str:
        """Sanitizes text extracted from third-party websites."""
        patterns = [
            r"ignore (all )?previous instructions",
            r"system prompt override",
            r"<\|im_start\|>",
            r"<\|im_end\|>",
        ]
        sanitized = text
        for p in patterns:
            sanitized = re.sub(p, "[FILTERED_WEB_INSTRUCTION]", sanitized, flags=re.IGNORECASE)
        return sanitized
