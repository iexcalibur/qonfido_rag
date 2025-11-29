"""
Qonfido RAG - LLM Generation
=============================
Generate responses using Claude API.
"""

import logging
import os
from typing import Any

from anthropic import Anthropic

from app.config import settings

logger = logging.getLogger(__name__)


class LLMGenerator:
    """
    Generate responses using Claude API.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-3-opus-20240229",
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ):
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        # Try: provided key -> settings config -> env var
        try:
            settings_key = settings.anthropic_api_key.get_secret_value()
        except Exception:
            settings_key = None
        
        self._api_key = (
            api_key 
            or settings_key
            or os.getenv("ANTHROPIC_API_KEY")
        )
        self._client = None

    @property
    def client(self) -> Anthropic:
        """Lazy load Anthropic client."""
        if self._client is None:
            if not self._api_key:
                raise ValueError("Anthropic API key not provided")
            self._client = Anthropic(api_key=self._api_key)
            logger.info("Anthropic client initialized")
        return self._client

    def generate(
        self,
        query: str,
        context: list[dict[str, Any]],
        system_prompt: str | None = None,
    ) -> str:
        """
        Generate a response for the query using retrieved context.
        
        Args:
            query: User's question
            context: List of retrieved documents with 'text', 'source', 'metadata'
            system_prompt: Optional custom system prompt
            
        Returns:
            Generated response string
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt()

        # Format context
        context_text = self._format_context(context)
        
        # Build user message
        user_message = f"""Based on the following context, answer the user's question.

## Context:
{context_text}

## Question:
{query}

## Instructions:
- Answer based ONLY on the provided context
- If the context contains fund data, include specific metrics (CAGR, Sharpe ratio, etc.)
- If you cannot answer from the context, say so
- Be concise but comprehensive
- For numerical queries, list the top funds with their metrics
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ],
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise

    def _get_default_system_prompt(self) -> str:
        """Get the default system prompt."""
        return """You are a helpful financial assistant for Qonfido, an AI Co-Pilot for Money.

Your role is to:
1. Answer questions about mutual funds and financial concepts
2. Provide accurate data from the retrieved context
3. Explain financial metrics clearly (CAGR, Sharpe ratio, volatility, etc.)
4. Be helpful but never give specific investment advice

Always cite the source of your information (FAQ or specific fund data)."""

    def _format_context(self, context: list[dict[str, Any]]) -> str:
        """Format retrieved documents as context string."""
        if not context:
            return "No relevant context found."
        
        formatted = []
        for i, doc in enumerate(context, 1):
            source = doc.get("source", "unknown")
            text = doc.get("text", "")
            
            # Add fund-specific metadata if available
            metadata = doc.get("metadata", {})
            extra_info = ""
            if source == "fund" and metadata:
                parts = []
                if metadata.get("fund_name"):
                    parts.append(f"Fund: {metadata['fund_name']}")
                if metadata.get("sharpe_ratio"):
                    parts.append(f"Sharpe: {metadata['sharpe_ratio']:.2f}")
                if metadata.get("cagr_3yr"):
                    parts.append(f"3Y CAGR: {metadata['cagr_3yr']:.2f}%")
                if parts:
                    extra_info = f" [{', '.join(parts)}]"
            
            formatted.append(f"[{i}] ({source.upper()}){extra_info}\n{text}")
        
        return "\n\n".join(formatted)


# =============================================================================
# Global Instance
# =============================================================================

_generator: LLMGenerator | None = None


def get_generator(**kwargs) -> LLMGenerator:
    """Get or create the global generator instance."""
    global _generator
    if _generator is None:
        # Use settings if not provided in kwargs
        kwargs.setdefault("model", settings.claude_model)
        kwargs.setdefault("max_tokens", settings.claude_max_tokens)
        kwargs.setdefault("temperature", settings.claude_temperature)
        _generator = LLMGenerator(**kwargs)
    return _generator
