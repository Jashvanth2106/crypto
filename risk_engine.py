"""
CryptoShield Risk Intelligence Engine

Prototype rule-based analysis for blockchain transactions.
"""


def calculate_risk(transactions):
    """Calculate an explainable prototype risk score."""

    total_transactions = len(transactions)

    incoming = 0
    outgoing = 0
    counterparties = set()
    large_transfers = 0

    for tx in transactions:

        if not isinstance(tx, dict):
            continue

        direction = str(tx.get("direction", "")).lower()

        if direction == "incoming":
            incoming += 1

        elif direction == "outgoing":
            outgoing += 1

        sender = (
            tx.get("from")
            or tx.get("from_address")
            or tx.get("sender")
        )

        receiver = (
            tx.get("to")
            or tx.get("to_address")
            or tx.get("receiver")
        )

        if sender:
            counterparties.add(str(sender).lower())

        if receiver:
            counterparties.add(str(receiver).lower())

        value = (
            tx.get("value")
            or tx.get("amount")
            or tx.get("value_eth")
            or tx.get("amount_eth")
            or 0
        )

        try:
            if float(value) > 1:
                large_transfers += 1
        except (TypeError, ValueError):
            pass

    score = 0
    reasons = []

    # -----------------------------------------
    # Transaction activity
    # -----------------------------------------

    if total_transactions >= 10:
        score += 25
        reasons.append(
            "High transaction activity detected"
        )

    elif total_transactions >= 5:
        score += 15
        reasons.append(
            "Moderate transaction activity detected"
        )

    # -----------------------------------------
    # Counterparty diversity
    # -----------------------------------------

    if len(counterparties) >= 8:
        score += 25
        reasons.append(
            "Large number of unique counterparties"
        )

    elif len(counterparties) >= 5:
        score += 15
        reasons.append(
            "Multiple unique counterparties detected"
        )

    # -----------------------------------------
    # Outgoing-heavy behavior
    # -----------------------------------------

    if outgoing > incoming:
        score += 15
        reasons.append(
            "Outgoing activity exceeds incoming activity"
        )

    # -----------------------------------------
    # Large transfers
    # -----------------------------------------

    if large_transfers >= 3:
        score += 20
        reasons.append(
            "Multiple large-value transfers detected"
        )

    elif large_transfers >= 1:
        score += 10
        reasons.append(
            "Large-value transfer detected"
        )

    # -----------------------------------------
    # Final score
    # -----------------------------------------

    score = min(score, 100)

    if score >= 70:
        level = "HIGH RISK"

    elif score >= 40:
        level = "MEDIUM RISK"

    else:
        level = "LOW RISK"

    if not reasons:
        reasons.append(
            "No major prototype risk indicators detected"
        )

    return {
        "score": score,
        "level": level,
        "reasons": reasons,
        "total_transactions": total_transactions,
        "incoming": incoming,
        "outgoing": outgoing,
        "counterparties": len(counterparties),
        "large_transfers": large_transfers,
    }
    