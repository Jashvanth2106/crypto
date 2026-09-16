"""
CryptoShield - Investigation Service

Connects wallet validation, blockchain retrieval,
and transaction analysis into one investigation workflow.
"""

from core.config import ETHERSCAN_API_KEY
from modules.ethereum import EthereumAdapter
from modules.transaction_analyzer import analyze_transactions


def investigate_wallet(address: str) -> dict:
    """
    Run a basic blockchain investigation for an Ethereum wallet.
    """

    if not address:
        raise ValueError("Wallet address cannot be empty.")

    adapter = EthereumAdapter(ETHERSCAN_API_KEY)

    transactions = adapter.get_transactions(address)

    analysis = analyze_transactions(
        transactions,
        address,
    )

    return {
        "wallet_address": address,
        "network": "Ethereum",
        "transactions": transactions,
        "analysis": analysis,
    }
    