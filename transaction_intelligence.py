from collections import Counter


def _get_address(tx, keys):
    """Return the first available address from a list of possible keys."""
    for key in keys:
        value = tx.get(key)
        if value:
            return str(value)
    return ""


def _get_value(tx):
    """Safely convert transaction value to float."""
    value = tx.get("value", 0)

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _get_timestamp(tx):
    """Safely get timestamp from a transaction."""
    for key in ["timestamp", "time", "block_timestamp", "date"]:
        if tx.get(key):
            return tx.get(key)

    return None


def analyze_transactions(transactions, wallet_address=None):
    """
    Analyze transactions for suspicious behavioral patterns.

    Returns:
        {
            "transactions_analyzed": int,
            "suspicious_transactions": int,
            "pattern_counts": dict,
            "findings": list,
            "summary": str
        }
    """

    if not transactions:
        return {
            "transactions_analyzed": 0,
            "suspicious_transactions": 0,
            "pattern_counts": {},
            "findings": [],
            "summary": "No transactions available for intelligence analysis."
        }

    # ---------------------------------------------------------
    # Normalize target wallet
    # ---------------------------------------------------------

    target = str(wallet_address).lower().strip() if wallet_address else ""

    # ---------------------------------------------------------
    # Basic transaction statistics
    # ---------------------------------------------------------

    values = [_get_value(tx) for tx in transactions]

    positive_values = [value for value in values if value > 0]

    average_value = (
        sum(positive_values) / len(positive_values)
        if positive_values
        else 0
    )

    # ---------------------------------------------------------
    # Determine large-transfer threshold
    # ---------------------------------------------------------

    # Use a minimum threshold of 1 so small demo datasets
    # can still produce useful intelligence.
    large_threshold = max(1.0, average_value * 2)

    # ---------------------------------------------------------
    # Counterparty analysis
    # ---------------------------------------------------------

    counterparties = []

    for tx in transactions:
        sender = _get_address(
            tx,
            ["from", "from_address", "sender"]
        )

        receiver = _get_address(
            tx,
            ["to", "to_address", "receiver"]
        )

        if sender and sender.lower() != target:
            counterparties.append(sender.lower())

        if receiver and receiver.lower() != target:
            counterparties.append(receiver.lower())

    counterparty_counts = Counter(counterparties)

    # ---------------------------------------------------------
    # Pattern counters
    # ---------------------------------------------------------

    pattern_counts = {
        "large_value_transfer": 0,
        "rapid_fund_movement": 0,
        "multiple_counterparties": 0,
        "repeated_counterparty": 0,
        "incoming_outgoing_flow": 0,
        "unusual_value_pattern": 0,
    }

    findings = []

    # ---------------------------------------------------------
    # Transaction-by-transaction analysis
    # ---------------------------------------------------------

    for index, tx in enumerate(transactions):

        value = _get_value(tx)

        sender = _get_address(
            tx,
            ["from", "from_address", "sender"]
        )

        receiver = _get_address(
            tx,
            ["to", "to_address", "receiver"]
        )

        sender_lower = sender.lower()
        receiver_lower = receiver.lower()

        flags = []
        explanations = []

        # -----------------------------------------------------
        # 1. Large-value transfer
        # -----------------------------------------------------

        if value >= large_threshold and value > 0:
            flags.append("large_value_transfer")

            explanations.append(
                f"Transfer value ({value:g}) is significantly "
                f"above the observed average ({average_value:g})."
            )

            pattern_counts["large_value_transfer"] += 1

        # -----------------------------------------------------
        # 2. Multiple counterparties
        # -----------------------------------------------------

        tx_counterparty = None

        if sender_lower == target:
            tx_counterparty = receiver_lower

        elif receiver_lower == target:
            tx_counterparty = sender_lower

        if tx_counterparty:
            if counterparty_counts[tx_counterparty] >= 3:

                flags.append("repeated_counterparty")

                explanations.append(
                    "The wallet interacts repeatedly with the same "
                    "counterparty."
                )

                pattern_counts["repeated_counterparty"] += 1

        # -----------------------------------------------------
        # 3. Incoming → outgoing flow
        # -----------------------------------------------------

        if target:

            is_outgoing = sender_lower == target
            is_incoming = receiver_lower == target

            if is_outgoing:
                previous_incoming = False

                for previous_tx in transactions[:index]:

                    previous_sender = _get_address(
                        previous_tx,
                        ["from", "from_address", "sender"]
                    ).lower()

                    previous_receiver = _get_address(
                        previous_tx,
                        ["to", "to_address", "receiver"]
                    ).lower()

                    if previous_receiver == target:
                        previous_incoming = True
                        break

                if previous_incoming:

                    flags.append("incoming_outgoing_flow")

                    explanations.append(
                        "An outgoing transfer occurs after an "
                        "incoming transfer to the investigated wallet."
                    )

                    pattern_counts["incoming_outgoing_flow"] += 1

        # -----------------------------------------------------
        # 4. Unusual value pattern
        # -----------------------------------------------------

        if average_value > 0:

            # Extremely large relative to average
            if value >= average_value * 5:

                flags.append("unusual_value_pattern")

                explanations.append(
                    "The transfer value is substantially higher "
                    "than the average observed transaction value."
                )

                pattern_counts["unusual_value_pattern"] += 1

        # -----------------------------------------------------
        # 5. Build finding
        # -----------------------------------------------------

        if flags:

            findings.append(
                {
                    "transaction_index": index + 1,
                    "transaction_hash": tx.get(
                        "hash",
                        tx.get("transaction_hash", "N/A")
                    ),
                    "from": sender,
                    "to": receiver,
                    "value": value,
                    "flags": flags,
                    "explanations": explanations,
                    "risk_indicator_count": len(flags),
                }
            )

    # ---------------------------------------------------------
    # Rapid movement heuristic
    # ---------------------------------------------------------

    # If timestamp data is available, look for consecutive
    # transactions that occur very close together.
    #
    # We keep this conservative because timestamp formats can
    # differ between blockchain APIs.

    timestamps = []

    for index, tx in enumerate(transactions):

        timestamp = _get_timestamp(tx)

        if timestamp is None:
            continue

        try:
            numeric_timestamp = float(timestamp)

            # Convert milliseconds → seconds if necessary.
            if numeric_timestamp > 10_000_000_000:
                numeric_timestamp /= 1000

            timestamps.append(
                (index, numeric_timestamp)
            )

        except (TypeError, ValueError):
            continue

    timestamps.sort(key=lambda item: item[1])

    rapid_indices = set()

    for i in range(1, len(timestamps)):

        previous_index, previous_time = timestamps[i - 1]
        current_index, current_time = timestamps[i]

        difference = current_time - previous_time

        # Transactions within 5 minutes.
        if 0 <= difference <= 300:

            rapid_indices.add(current_index)

    for finding in findings:

        tx_index = finding["transaction_index"] - 1

        if tx_index in rapid_indices:

            if "rapid_fund_movement" not in finding["flags"]:

                finding["flags"].append(
                    "rapid_fund_movement"
                )

                finding["explanations"].append(
                    "This transaction occurred shortly after "
                    "another observed transaction."
                )

                finding["risk_indicator_count"] = len(
                    finding["flags"]
                )

                pattern_counts["rapid_fund_movement"] += 1

    # ---------------------------------------------------------
    # Additional heuristic:
    # Multiple counterparties
    # ---------------------------------------------------------

    unique_counterparties = len(counterparty_counts)

    if unique_counterparties >= 5:

        pattern_counts["multiple_counterparties"] = 1

        findings.append(
            {
                "transaction_index": None,
                "transaction_hash": "WALLET_LEVEL",
                "from": target,
                "to": "",
                "value": 0,
                "flags": ["multiple_counterparties"],
                "explanations": [
                    f"The investigated wallet interacted with "
                    f"{unique_counterparties} unique counterparties."
                ],
                "risk_indicator_count": 1,
            }
        )

    # ---------------------------------------------------------
    # Suspicious transaction count
    # ---------------------------------------------------------

    suspicious_transaction_indexes = set()

    for finding in findings:

        if finding["transaction_index"] is not None:

            suspicious_transaction_indexes.add(
                finding["transaction_index"]
            )

    suspicious_transactions = len(
        suspicious_transaction_indexes
    )

    # ---------------------------------------------------------
    # Summary
    # ---------------------------------------------------------

    active_patterns = [
        name
        for name, count in pattern_counts.items()
        if count > 0
    ]

    if not active_patterns:

        summary = (
            "No major transaction-level behavioral patterns "
            "were detected in the available data."
        )

    else:

        readable_patterns = ", ".join(
            name.replace("_", " ")
            for name in active_patterns
        )

        summary = (
            f"Detected {len(active_patterns)} pattern categories: "
            f"{readable_patterns}."
        )

    return {
        "transactions_analyzed": len(transactions),
        "suspicious_transactions": suspicious_transactions,
        "pattern_counts": pattern_counts,
        "findings": findings,
        "summary": summary,
        "average_transaction_value": average_value,
        "large_transfer_threshold": large_threshold,
        "unique_counterparties": unique_counterparties,
    }