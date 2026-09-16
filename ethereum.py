"""
CryptoShield - Ethereum Blockchain Adapter

Retrieves Ethereum transactions from Etherscan
and normalizes them for the investigation engine.
"""

import requests


class EthereumAdapter:

    BASE_URL = "https://api.etherscan.io/v2/api"
    CHAIN_ID = "1"

    def __init__(self, api_key=None):
        self.api_key = api_key

    # =========================================================
    # VALIDATION
    # =========================================================

    def validate_address(self, address):
        """Basic Ethereum wallet address validation."""

        if not address:
            raise ValueError(
                "Wallet address cannot be empty."
            )

        address = address.strip()

        if not address.startswith("0x"):
            raise ValueError(
                "Invalid Ethereum address. Address must start with 0x."
            )

        if len(address) != 42:
            raise ValueError(
                "Invalid Ethereum address length."
            )

        return address

    # =========================================================
    # WEI → ETH
    # =========================================================

    @staticmethod
    def wei_to_eth(value):
        """Convert Wei to ETH safely."""

        try:
            return float(value) / 10**18
        except (TypeError, ValueError):
            return 0.0

    # =========================================================
    # GET TRANSACTIONS
    # =========================================================

    def get_transactions(self, address):

        address = self.validate_address(address)

        if not self.api_key:
            raise RuntimeError(
                "Etherscan API key is not configured."
            )

        params = {
            "chainid": self.CHAIN_ID,
            "module": "account",
            "action": "txlist",
            "address": address,
            "startblock": "0",
            "endblock": "99999999",
            "page": "1",
            "offset": "100",
            "sort": "asc",
            "apikey": self.api_key,
        }

        try:

            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=20,
            )

            response.raise_for_status()

        except requests.RequestException as exc:

            raise RuntimeError(
                f"Unable to connect to Etherscan: {exc}"
            ) from exc

        try:

            data = response.json()

        except ValueError as exc:

            raise RuntimeError(
                "Etherscan returned an invalid JSON response."
            ) from exc

        # -----------------------------------------------------
        # API ERROR HANDLING
        # -----------------------------------------------------

        if data.get("status") == "0":

            result = data.get("result", "")

            if isinstance(result, str):

                if (
                    "No transactions" in result
                    or "No transactions found" in result
                ):
                    return []

            raise RuntimeError(
                f"Etherscan API error: {result}"
            )

        raw_transactions = data.get(
            "result",
            []
        )

        if not isinstance(raw_transactions, list):
            return []

        # -----------------------------------------------------
        # NORMALIZE
        # -----------------------------------------------------

        normalized = []

        wallet = address.lower()

        for tx in raw_transactions:

            if not isinstance(tx, dict):
                continue

            sender = str(
                tx.get("from", "")
            ).strip()

            receiver = str(
                tx.get("to", "")
            ).strip()

            if not sender or not receiver:
                continue

            sender_lower = sender.lower()
            receiver_lower = receiver.lower()

            # Determine transaction direction
            if sender_lower == wallet:

                direction = "outgoing"

            elif receiver_lower == wallet:

                direction = "incoming"

            else:

                direction = "unknown"

            # Convert Wei to ETH
            value_eth = self.wei_to_eth(
                tx.get("value", 0)
            )

            normalized_transaction = {

                # -------------------------------------------------
                # CORE IDENTIFIERS
                # -------------------------------------------------

                "hash": tx.get(
                    "hash",
                    ""
                ),

                "tx_hash": tx.get(
                    "hash",
                    ""
                ),

                "block_number": tx.get(
                    "blockNumber",
                    ""
                ),

                # -------------------------------------------------
                # ADDRESSES
                # -------------------------------------------------

                "from": sender,

                "to": receiver,

                "from_address": sender,

                "to_address": receiver,

                # -------------------------------------------------
                # VALUE
                # -------------------------------------------------

                "value": value_eth,

                "amount": value_eth,

                "value_eth": value_eth,

                # Keep original Wei value too
                "value_wei": tx.get(
                    "value",
                    "0"
                ),

                # -------------------------------------------------
                # DIRECTION
                # -------------------------------------------------

                "direction": direction,

                # -------------------------------------------------
                # TIMESTAMP
                # -------------------------------------------------

                "timestamp": tx.get(
                    "timeStamp",
                    ""
                ),

                # -------------------------------------------------
                # GAS / FEE INFORMATION
                # -------------------------------------------------

                "gas": tx.get(
                    "gas",
                    ""
                ),

                "gas_price": tx.get(
                    "gasPrice",
                    ""
                ),

                "gas_used": tx.get(
                    "gasUsed",
                    ""
                ),

                # -------------------------------------------------
                # TRANSACTION STATUS
                # -------------------------------------------------

                "is_error": tx.get(
                    "isError",
                    "0"
                ),

                "tx_receipt_status": tx.get(
                    "txreceipt_status",
                    ""
                ),

                # -------------------------------------------------
                # CONTRACT / METHOD DATA
                # -------------------------------------------------

                "method_id": tx.get(
                    "methodId",
                    ""
                ),

                "function_name": tx.get(
                    "functionName",
                    ""
                ),

                # -------------------------------------------------
                # ORIGINAL RAW DATA
                # -------------------------------------------------

                "raw": tx,
            }

            normalized.append(
                normalized_transaction
            )

        return normalized
        