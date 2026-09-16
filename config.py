"""
CryptoShield configuration management.

Secrets are loaded from environment variables rather than
being hard-coded into the application.
"""

import os

from dotenv import load_dotenv


# Load variables from the local .env file.
load_dotenv()


def get_env(name: str, required: bool = False) -> str | None:
    """
    Read an environment variable.

    Args:
        name: Environment variable name.
        required: Whether the variable must exist.

    Returns:
        The variable value, or None if it is not available.

    Raises:
        RuntimeError: If a required variable is missing.
    """

    value = os.getenv(name)

    if required and not value:
        raise RuntimeError(
            f"Required configuration '{name}' is missing."
        )

    return value


ETHERSCAN_API_KEY = get_env("ETHERSCAN_API_KEY")