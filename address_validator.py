"""
CryptoShield - Wallet Address Validation

This module performs basic validation of cryptocurrency wallet
addresses before they enter the investigation pipeline.
"""

import re


def validate_evm_address(address: str) -> dict:
    """
    Validate an EVM-compatible cryptocurrency address.

    EVM chains include:
    Ethereum
    BNB Chain
    Polygon
    Arbitrum
    Base
    Optimism

    Returns a dictionary containing the validation result.
    """

    address = address.strip()

    # Empty input
    if not address:
        return {
            "valid": False,
            "type": "EVM",
            "message": "Wallet address cannot be empty.",
        }

    # EVM addresses start with 0x and contain 40 hexadecimal characters.
    pattern = r"^0x[a-fA-F0-9]{40}$"

    if not re.fullmatch(pattern, address):
        return {
            "valid": False,
            "type": "EVM",
            "message": "Invalid EVM wallet address format.",
        }

    return {
        "valid": True,
        "type": "EVM",
        "message": "Valid EVM wallet address.",
        "address": address,
    }
if __name__ == "__main__":
    test_address = "0x0000000000000000000000000000000000000000"

    result = validate_evm_address(test_address)

    print(result)