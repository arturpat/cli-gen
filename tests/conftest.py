import pytest

from config import system_prompt, temperature
from utils import ChatWithMemory, get_api_key


@pytest.fixture(scope="session")
def openai_api_key():
    get_api_key()


@pytest.fixture()
def chat(openai_api_key):
    return ChatWithMemory(system_prompt=system_prompt, temperature=temperature)
