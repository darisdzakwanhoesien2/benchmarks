"""Utility helpers for resolving a Gradio Space URL.

This module is used by the API clients (e.g., ABSA and ESG Data) to determine
which Hugging Face Space URL to talk to.

Resolution order:
  1) explicit ``space_url`` argument
  2) environment variable (e.g. ``HF_ESGDATA_SPACE``)
  3) optional ``default`` value

If no URL can be resolved, a ``ValueError`` is raised to help the user fix their
configuration.
"""

from __future__ import annotations

import os
from typing import Optional


def resolve_space_url(
    space_url: Optional[str] = None,
    env_var: Optional[str] = None,
    default: Optional[str] = None,
) -> str:
    """Resolve the Gradio Space URL to use.

    Args:
        space_url: An explicit URL passed in by the caller.
        env_var: Name of the environment variable to check if ``space_url`` is not set.
        default: A fallback default URL to use if neither ``space_url`` nor ``env_var`` is set.

    Returns:
        The resolved Space URL string.

    Raises:
        ValueError: If no URL could be resolved.
    """

    if space_url:
        return space_url.strip()

    if env_var:
        env_value = os.getenv(env_var)
        if env_value:
            return env_value.strip()

    if default:
        return default

    raise ValueError(
        "No Gradio Space URL could be resolved. "
        "Provide `space_url`, set the environment variable `" + (env_var or "<ENV_VAR>") + "`, "
        "or add it to a `.env` file in this repo (e.g. `.env.example`)."
    )
