"""
CryptoShield - Transaction Analyzer

Converts raw blockchain transactions into useful
investigation statistics.
"""


def analyze_transactions(
    transactions: list[dict],
    suspect_address: str,
) -> dict:
    """
    Analyze transactions associated with a suspect wallet.

    Returns investigation-friendly statistics.
    """

    suspect_address = suspect_address.lower()

    incoming = []
    outgoing = []

    received_wei = 0
    sent_wei = 0

    unique_addresses = set()

    for tx in transactions:

        sender = str(tx.get("from") or "").lower()
        receiver = str(tx.get("to") or "").lower()

        try:
            value_wei = int(tx.get("value", "0") or 0)
        except (ValueError, TypeError):
            value_wei = 0

        # Incoming transaction
        if receiver == suspect_address:

            incoming.append(tx)

            received_wei += value_wei

            if sender:
                unique_addresses.add(sender)

        # Outgoing transaction
        if sender == suspect_address:

            outgoing.append(tx)

            sent_wei += value_wei

            if receiver:
                unique_addresses.add(receiver)

    return {
        "total_transactions": len(transactions),
        "incoming_transactions": len(incoming),
        "outgoing_transactions": len(outgoing),
        "total_received_wei": received_wei,
        "total_sent_wei": sent_wei,
        "unique_counterparties": len(unique_addresses),
        "incoming": incoming,
        "outgoing": outgoing,
    }


def wei_to_eth(value_wei: int) -> float:
    """
    Convert Wei to Ether.
    """

    return value_wei / 10**18

if __name__ == "__main__":

    suspect = "0x1111111111111111111111111111111111111111"

    test_transactions = [
        {
            "hash": "tx1",
            "from": "0x2222222222222222222222222222222222222222",
            "to": suspect,
            "value": "1000000000000000000",
        },
        {
            "hash": "tx2",
            "from": suspect,
            "to": "0x3333333333333333333333333333333333333333",
            "value": "500000000000000000",
        },
    ]

    result = analyze_transactions(
        test_transactions,
        suspect,
    )

    print("Total transactions:", result["total_transactions"])
    print("Incoming:", result["incoming_transactions"])
    print("Outgoing:", result["outgoing_transactions"])
    print(
        "Received ETH:",
        wei_to_eth(result["total_received_wei"]),
    )
    print(
        "Sent ETH:",
        wei_to_eth(result["total_sent_wei"]),
    )
    print(
        "Unique counterparties:",
        result["unique_counterparties"],
    )