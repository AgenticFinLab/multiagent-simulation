# utils/llm_init.py
import httpx
from openai import OpenAI


def init_llm_client(config):
    if config["provider"] == "openai":

        http_client = httpx.Client(
            timeout=httpx.Timeout(60.0, connect=30.0),
            limits=httpx.Limits(max_connections=10)
        )

        client = OpenAI(
            api_key=config["api_key"],
            base_url=config.get("base_url"),  
            http_client=http_client,
            max_retries=3
        )
        return client, config["model"]