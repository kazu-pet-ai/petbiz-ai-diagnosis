import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


APP_NAME = "PetBiz AI 60秒経営診断"


def _setting(name: str, default: str) -> str:
    """Read Secrets when present, then environment variables, then a safe default."""
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except StreamlitSecretNotFoundError:
        return os.getenv(name, default)


CTA_URL = _setting("CTA_URL", "https://forms.gle/f1thoy8S9MgmjMg1A")
