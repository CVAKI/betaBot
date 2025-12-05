"""
LLM Client - Google Gemini API Integration
Handles connection and communication with Gemini API
"""

import google.generativeai as genai
import os
import time
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import config


class GeminiClient:
    """Client for Google Gemini API"""

    def __init__(self):
        """Initialize Gemini client"""
        self.api_key = config.GEMINI_API_KEY
        if not self.api_key:
            self.api_key = os.getenv('GEMINI_API_KEY', '')

        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable "
                "or add it to config.py"
            )

        # Configure Gemini
        genai.configure(api_key=self.api_key)

        # Initialize model
        self.model_name = config.GEMINI_MODEL
        self.model = genai.GenerativeModel(self.model_name)

        # Generation config
        self.generation_config = {
            'temperature': config.LLM_TEMPERATURE,
            'top_p': 0.95,
            'top_k': 40,
            'max_output_tokens': config.LLM_MAX_TOKENS,
        }

        # Safety settings (allow creative content)
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_NONE"
            },
        ]

        # Rate limiting
        self.rate_limit_calls = config.LLM_RATE_LIMIT_CALLS
        self.rate_limit_window = config.LLM_RATE_LIMIT_WINDOW
        self.call_timestamps = []

        # Connection status
        self.is_connected = False
        self._test_connection()

    def _test_connection(self) -> bool:
        """Test connection to Gemini API"""
        try:
            # Simple test prompt
            response = self.model.generate_content(
                "Hello",
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            self.is_connected = True
            return True
        except Exception as e:
            print(f"Warning: Gemini API connection failed: {e}")
            self.is_connected = False
            return False

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = time.time()

        # Remove old timestamps outside the window
        self.call_timestamps = [
            ts for ts in self.call_timestamps
            if now - ts < self.rate_limit_window
        ]

        # Check if we can make another call
        if len(self.call_timestamps) >= self.rate_limit_calls:
            return False

        return True

    def _wait_for_rate_limit(self):
        """Wait until we can make another API call"""
        while not self._check_rate_limit():
            time.sleep(1)

    def generate_response(self, prompt: str, retry_count: int = 3) -> Optional[str]:
        """
        Generate response from Gemini

        Args:
            prompt: Input prompt
            retry_count: Number of retries on failure

        Returns:
            Generated text or None on failure
        """
        if not self.is_connected:
            print("Warning: Gemini API not connected. Attempting reconnection...")
            if not self._test_connection():
                return None

        # Wait for rate limit if needed
        self._wait_for_rate_limit()

        for attempt in range(retry_count):
            try:
                # Record API call
                self.call_timestamps.append(time.time())

                # Generate content
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config,
                    safety_settings=self.safety_settings
                )

                # Extract text
                if response and response.text:
                    return response.text.strip()
                else:
                    print(f"Warning: Empty response from Gemini (attempt {attempt + 1})")

            except Exception as e:
                print(f"Error generating response (attempt {attempt + 1}/{retry_count}): {e}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None

        return None

    def generate_streaming(self, prompt: str):
        """
        Generate streaming response (for future enhancements)

        Args:
            prompt: Input prompt

        Yields:
            Text chunks as they arrive
        """
        if not self.is_connected:
            return

        self._wait_for_rate_limit()

        try:
            self.call_timestamps.append(time.time())

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings,
                stream=True
            )

            for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            print(f"Error in streaming generation: {e}")

    def check_connection(self) -> bool:
        """Check if API is connected"""
        return self.is_connected

    def get_model_info(self) -> Dict:
        """Get information about current model"""
        return {
            'model_name': self.model_name,
            'max_tokens': config.LLM_MAX_TOKENS,
            'temperature': config.LLM_TEMPERATURE,
            'is_connected': self.is_connected
        }

    def __repr__(self):
        status = "Connected" if self.is_connected else "Disconnected"
        return f"GeminiClient(model={self.model_name}, status={status})"


class LLMClient:
    """
    Unified LLM Client that can work with different providers
    Currently configured for Gemini
    """

    def __init__(self):
        """Initialize LLM client based on config"""
        self.provider = config.LLM_PROVIDER

        if self.provider == 'gemini':
            self.client = GeminiClient()
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str) -> Optional[str]:
        """Generate response"""
        return self.client.generate_response(prompt)

    def is_connected(self) -> bool:
        """Check connection status"""
        return self.client.check_connection()

    def get_info(self) -> Dict:
        """Get client information"""
        return self.client.get_model_info()