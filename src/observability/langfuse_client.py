import os
from langfuse import Langfuse
from dotenv import load_dotenv

load_dotenv()

class LangfuseClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LangfuseClient, cls).__new__(cls)
            cls._instance.client = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
                host=os.getenv("LANGFUSE_BASE_URL", "https://cloud.langfuse.com")
            )
        return cls._instance

    def create_trace(self, name: str, session_id: str):
        return self.client.trace(name=name, session_id=session_id)

    def get_prompt(self, prompt_name: str, cache_seconds: int = 600):
        return self.client.get_prompt(prompt_name, cache_seconds=cache_seconds)

langfuse_client = LangfuseClient()
