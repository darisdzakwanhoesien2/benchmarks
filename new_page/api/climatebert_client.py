import os
from typing import Any, Optional
from gradio_client import Client

DEFAULT_SPACE = "https://darisdzakwanhoesien-climatebert-multi-model-demo-8aae81e.hf.space/"

class ClimateBERTClient:
    """
    Minimal wrapper around gradio_client.Client for the ClimateBERT demo space.
    Usage:
        api = ClimateBERTClient()  # reads CLIMATEBERT_SPACE_URL or uses DEFAULT_SPACE
        resp = api.predict_all_models("Some text")
    """
    def __init__(self, space_url: Optional[str] = None, timeout: int = 60, hf_token: Optional[str] = None):
        self.space_url = (space_url or os.getenv("CLIMATEBERT_SPACE_URL") or DEFAULT_SPACE).rstrip("/") + "/"
        self.timeout = timeout
        self.hf_token = hf_token or os.getenv("HF_TOKEN") or None
        self._client: Optional[Client] = None

    def _ensure_client(self) -> None:
        """Lazy-init the gradio Client. Raises any connection exceptions to caller."""
        if self._client is None:
            # pass hf_token if required, and set a longer timeout
            kwargs = {"timeout": self.timeout}
            if self.hf_token:
                kwargs["hf_token"] = self.hf_token
            self._client = Client(self.space_url, **kwargs)

    def predict_all_models(self, text: str) -> Any:
        """
        Call the space endpoint that returns predictions for all models.
        Uses API name '/predict_all_models'.
        """
        self._ensure_client()
        # pass named argument to match the space input component
        return self._client.predict(text=text, api_name="/predict_all_models", timeout=self.timeout)

    def predict(self, text: str, api_name: str = "/predict", **kwargs) -> Any:
        """
        Generic helper to call any named endpoint on the space.
        Pass extra kwargs required by the endpoint (e.g. model=...).
        """
        self._ensure_client()
        # pass text as named parameter by default
        return self._client.predict(text=text, api_name=api_name, timeout=self.timeout, **kwargs)

    @property
    def available_models(self) -> list:
        """
        Best-effort: call a '/list_models' endpoint if available, otherwise return [].
        """
        try:
            self._ensure_client()
            resp = self._client.predict("", api_name="/list_models")
            if isinstance(resp, dict):
                return list(resp.keys())
            if isinstance(resp, list):
                return resp
        except Exception:
            pass
        return []

client = ClimateBERTClient()

# Example usage in a function
def predict_text(text: str):
    try:
        out = client.predict_all_models(text)
        print(out)
    except Exception as e:
        print(f"Prediction failed: {e}")
