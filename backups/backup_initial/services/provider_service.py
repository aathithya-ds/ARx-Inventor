"""
ARX INVENTOR - Provider Service
Manages Google Gemini, OpenAI, and Anthropic Claude configurations,
connection tests, rate limits, secure credential handling, and demo simulations.
"""

import os
import time
from typing import Dict, Any, Tuple, Optional
from config.settings import settings

class ProviderStatus:
    MISSING_KEY = "Missing Key"
    CONFIGURED = "Configured (Untested)"
    CONNECTED = "Connected"
    ERROR = "Connection Error"
    SIMULATED = "Simulated (Demo Mode)"

class ProviderService:
    """Manages multi-provider LLM integrations with safe connection testing."""

    def __init__(self):
        self._provider_status = {
            "gemini": ProviderStatus.CONFIGURED if settings.GEMINI_API_KEY else ProviderStatus.MISSING_KEY,
            "openai": ProviderStatus.CONFIGURED if settings.OPENAI_API_KEY else ProviderStatus.MISSING_KEY,
            "anthropic": ProviderStatus.CONFIGURED if settings.ANTHROPIC_API_KEY else ProviderStatus.MISSING_KEY,
        }
        self._last_errors = {
            "gemini": None,
            "openai": None,
            "anthropic": None
        }

    def mask_key(self, key: str) -> str:
        """Safely masks API key for UI display without exposing secret."""
        if not key or len(key) < 8:
            return "Not set"
        return f"{key[:4]}...{key[-4:]}"

    def get_provider_details(self) -> Dict[str, Dict[str, Any]]:
        """Returns provider state, model names, and masked keys for the UI."""
        return {
            "gemini": {
                "name": "Google Gemini",
                "role": "Research Planner & Scope Formulation",
                "model": settings.GEMINI_MODEL,
                "masked_key": self.mask_key(settings.GEMINI_API_KEY),
                "has_key": bool(settings.GEMINI_API_KEY),
                "status": self._provider_status["gemini"],
                "last_error": self._last_errors["gemini"]
            },
            "openai": {
                "name": "OpenAI",
                "role": "Evidence Extraction, Analysis & Synthesis",
                "model": settings.OPENAI_MODEL,
                "masked_key": self.mask_key(settings.OPENAI_API_KEY),
                "has_key": bool(settings.OPENAI_API_KEY),
                "status": self._provider_status["openai"],
                "last_error": self._last_errors["openai"]
            },
            "anthropic": {
                "name": "Anthropic Claude",
                "role": "Citation Quality Review & Audit",
                "model": settings.ANTHROPIC_MODEL,
                "masked_key": self.mask_key(settings.ANTHROPIC_API_KEY),
                "has_key": bool(settings.ANTHROPIC_API_KEY),
                "status": self._provider_status["anthropic"],
                "last_error": self._last_errors["anthropic"]
            }
        }

    def test_gemini_connection(self) -> Tuple[bool, str]:
        """Tests Google Gemini connectivity with a safe minimal API call."""
        if not settings.GEMINI_API_KEY:
            self._provider_status["gemini"] = ProviderStatus.MISSING_KEY
            self._last_errors["gemini"] = "GEMINI_API_KEY is not configured in environment"
            return False, self._last_errors["gemini"]

        try:
            from google import genai
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
            # Safe minimal ping call
            response = client.models.generate_content(
                model=settings.GEMINI_MODEL,
                contents="Ping. Respond with 'PONG'."
            )
            if response and response.text:
                self._provider_status["gemini"] = ProviderStatus.CONNECTED
                self._last_errors["gemini"] = None
                return True, f"Successfully connected to Gemini model '{settings.GEMINI_MODEL}'"
            else:
                raise ValueError("Empty response received from Gemini API")
        except Exception as e:
            self._provider_status["gemini"] = ProviderStatus.ERROR
            self._last_errors["gemini"] = str(e)
            return False, f"Gemini connection failed: {str(e)}"

    def test_openai_connection(self) -> Tuple[bool, str]:
        """Tests OpenAI connectivity with a safe minimal models list call."""
        if not settings.OPENAI_API_KEY:
            self._provider_status["openai"] = ProviderStatus.MISSING_KEY
            self._last_errors["openai"] = "OPENAI_API_KEY is not configured in environment"
            return False, self._last_errors["openai"]

        try:
            import openai
            client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            # Safe minimal call: list models
            client.models.list()
            self._provider_status["openai"] = ProviderStatus.CONNECTED
            self._last_errors["openai"] = None
            return True, f"Successfully connected to OpenAI (Model: '{settings.OPENAI_MODEL}')"
        except Exception as e:
            self._provider_status["openai"] = ProviderStatus.ERROR
            self._last_errors["openai"] = str(e)
            return False, f"OpenAI connection failed: {str(e)}"

    def test_anthropic_connection(self) -> Tuple[bool, str]:
        """Tests Anthropic Claude connectivity with a safe minimal ping call."""
        if not settings.ANTHROPIC_API_KEY:
            self._provider_status["anthropic"] = ProviderStatus.MISSING_KEY
            self._last_errors["anthropic"] = "ANTHROPIC_API_KEY is not configured in environment"
            return False, self._last_errors["anthropic"]

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
            resp = client.messages.create(
                model=settings.ANTHROPIC_MODEL,
                max_tokens=10,
                messages=[{"role": "user", "content": "Ping"}]
            )
            if resp and resp.content:
                self._provider_status["anthropic"] = ProviderStatus.CONNECTED
                self._last_errors["anthropic"] = None
                return True, f"Successfully connected to Anthropic Claude model '{settings.ANTHROPIC_MODEL}'"
            else:
                raise ValueError("Empty response received from Anthropic API")
        except Exception as e:
            self._provider_status["anthropic"] = ProviderStatus.ERROR
            self._last_errors["anthropic"] = str(e)
            return False, f"Anthropic connection failed: {str(e)}"

    def generate_completion(
        self,
        provider: str,
        prompt: str,
        system_prompt: str = "",
        demo_mode: bool = False,
        demo_task: str = "generic"
    ) -> Dict[str, Any]:
        """
        Executes completion on configured provider with graceful fallback disclosure.
        provider: 'gemini' | 'openai' | 'anthropic'
        """
        # If demo mode is active or requested, run deterministic high-quality simulation
        if demo_mode or settings.DEMO_MODE:
            return self._run_simulation(provider, prompt, demo_task)

        provider_clean = provider.lower()

        # 1. Google Gemini
        if provider_clean == "gemini":
            if not settings.GEMINI_API_KEY:
                # Return disclosure fallback if enabled
                return self._run_simulation("gemini", prompt, demo_task, simulated_reason="GEMINI_API_KEY missing")
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                full_content = f"System: {system_prompt}\n\nUser: {prompt}" if system_prompt else prompt
                resp = client.models.generate_content(
                    model=settings.GEMINI_MODEL,
                    contents=full_content
                )
                return {
                    "provider": "gemini",
                    "model": settings.GEMINI_MODEL,
                    "text": resp.text,
                    "simulated": False,
                    "error": None
                }
            except Exception as e:
                return self._run_simulation("gemini", prompt, demo_task, simulated_reason=f"Gemini API error: {str(e)}")

        # 2. OpenAI
        elif provider_clean == "openai":
            if not settings.OPENAI_API_KEY:
                return self._run_simulation("openai", prompt, demo_task, simulated_reason="OPENAI_API_KEY missing")
            try:
                import openai
                client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                resp = client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=0.2
                )
                return {
                    "provider": "openai",
                    "model": settings.OPENAI_MODEL,
                    "text": resp.choices[0].message.content,
                    "simulated": False,
                    "error": None
                }
            except Exception as e:
                return self._run_simulation("openai", prompt, demo_task, simulated_reason=f"OpenAI API error: {str(e)}")

        # 3. Anthropic Claude
        elif provider_clean == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                return self._run_simulation("anthropic", prompt, demo_task, simulated_reason="ANTHROPIC_API_KEY missing")
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                resp = client.messages.create(
                    model=settings.ANTHROPIC_MODEL,
                    system=system_prompt if system_prompt else None,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": prompt}]
                )
                text_content = resp.content[0].text if resp.content else ""
                return {
                    "provider": "anthropic",
                    "model": settings.ANTHROPIC_MODEL,
                    "text": text_content,
                    "simulated": False,
                    "error": None
                }
            except Exception as e:
                return self._run_simulation("anthropic", prompt, demo_task, simulated_reason=f"Anthropic API error: {str(e)}")

        else:
            raise ValueError(f"Unknown provider '{provider}'")

    def _run_simulation(
        self,
        provider: str,
        prompt: str,
        demo_task: str,
        simulated_reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Produces deterministic, verifiable simulated research response."""
        reason_msg = f" (Disclosed Fallback: {simulated_reason})" if simulated_reason else " (Demo Mode Active)"
        
        return {
            "provider": provider,
            "model": f"{provider}-simulated",
            "simulated": True,
            "simulated_reason": simulated_reason or "Demo Mode Enabled",
            "text": f"[SIMULATED - {provider.upper()}]{reason_msg}\n\nExecution simulated based on research inputs.",
            "error": None
        }
