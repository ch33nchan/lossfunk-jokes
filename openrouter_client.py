
import requests
import json
from typing import List, Dict, Any, Optional

OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

class OpenRouterClient:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("OpenRouter API key is required.")
        self.api_key = api_key
        self.site_url = "YOUR_SITE_URL_HERE" 
        self.site_name = "JokeBot" 

    def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url, 
            "X-Title": self.site_name,      
        }
        try:
            response = requests.post(OPENROUTER_API_URL, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err} - {response.text}")
            raise
        except requests.exceptions.RequestException as req_err:
            print(f"Request exception occurred: {req_err}")
            raise
        except json.JSONDecodeError:
            print(f"Failed to decode JSON response: {response.text}")
            raise

    def get_completion(self,
                       model_name: str,
                       messages: List],
                       temperature: float = 0.7,
                       max_tokens: int = 500,
                       response_format: Optional] = None) -> Optional[str]:
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        try:
            response_data = self._make_request(payload)
            if response_data and "choices" in response_data and len(response_data["choices"]) > 0:
                choice = response_data["choices"]
                if "message" in choice and "content" in choice["message"]:
                    return choice["message"]["content"].strip()
                elif "delta" in choice and "content" in choice["delta"]: # For streaming
                    return choice["delta"]["content"].strip()
            return None
        except Exception as e:
            print(f"Error in get_completion for model {model_name}: {e}")
            return None