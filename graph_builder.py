"""
CryptoShield - Premium Fund Flow Graph

Creates an investigator-focused interactive blockchain graph.
"""

from streamlit_agraph import Node, Edge


# =========================================================
# DESIGN SYSTEM
# =========================================================

COLORS = {
    "suspect": "#ff3b5c",
    "wallet": "#3b82f6",
    "intermediary": "#f59e0b",
    "vasp": "#a855f7",
    "text": "#e5e7eb",
    "edge": "#64748b",
}


def short_address(address: str) -> str:
    """Create a compact display address."""

    if len(address) <= 14:
        return address

    return f"{address[:6]}...{address[-4:]}"


def create_graph_elements(
    transactions: list[dict],
    suspect_address: str,
):
    """
    Convert blockchain transactions into premium
    visual graph elements.
    """

    suspect_address = suspect_address.lower()

    nodes = []
    edges = []

    node_ids = set()

    for tx in transactions:

        sender = str(tx.get("from") or "").lower()
        receiver = str(tx.get("to") or "").lower()

        if not sender or not receiver:
            continue

        if sender == receiver:
            continue

        # =================================================
        # TRANSACTION VALUE
        # =================================================

        try:
            value_wei = int(tx.get("value", "0") or 0)
        except (ValueError, TypeError):
            value_wei = 0

        value_eth = value_wei / 10**18

        # =================================================
        # SENDER NODE
        # =================================================

        if sender not in node_ids:

            if sender == suspect_address:

                role = "SUSPECT WALLET"
                color = COLORS["suspect"]
                size = 42

                label = "🔴 SUSPECT"

            else:

                role = "WALLET"
                color = COLORS["wallet"]
                size = 25

                label = short_address(sender)

            nodes.append(
                Node(
                    id=sender,
                    label=label,
                    size=size,
                    color={
                        "background": color,
                        "border": "#ffffff",
                        "highlight": {
                            "background": color,
                            "border": "#ffffff",
                        },
                        "hover": {
                            "background": color,
                            "border": "#ffffff",
                        },
                    },
                    borderWidth=2,
                    shadow={
                        "enabled": True,
                        "color": color,
                        "size": 22,
                        "x": 0,
                        "y": 0,
                    },
                    font={
                        "color": COLORS["text"],
                        "size": 15,
                        "face": "Inter, Arial, sans-serif",
                        "bold": sender == suspect_address,
                    },
                    title=(
                        f"<b>{role}</b><br>"
                        f"Address: {sender}<br>"
                        f"Outgoing value: {value_eth:.4f} ETH"
                    ),
                )
            )

            node_ids.add(sender)

        # =================================================
        # RECEIVER NODE
        # =================================================

        if receiver not in node_ids:

            nodes.append(
                Node(
                    id=receiver,
                    label=short_address(receiver),
                    size=25,
                    color={
                        "background": COLORS["wallet"],
                        "border": "#93c5fd",
                        "highlight": {
                            "background": COLORS["wallet"],
                            "border": "#ffffff",
                        },
                        "hover": {
                            "background": COLORS["wallet"],
                            "border": "#ffffff",
                        },
                    },
                    borderWidth=2,
                    shadow={
                        "enabled": True,
                        "color": COLORS["wallet"],
                        "size": 16,
                        "x": 0,
                        "y": 0,
                    },
                    font={
                        "color": COLORS["text"],
                        "size": 14,
                        "face": "Inter, Arial, sans-serif",
                    },
                    title=(
                        f"<b>WALLET</b><br>"
                        f"Address: {receiver}<br>"
                        f"Received value: {value_eth:.4f} ETH"
                    ),
                )
            )

            node_ids.add(receiver)

        # =================================================
        # TRANSACTION EDGE
        # =================================================

        edges.append(
            Edge(
                source=sender,
                target=receiver,
                label=(
                    f"{value_eth:.4f} ETH"
                    if value_eth > 0
                    else "0 ETH"
                ),
                color={
                    "color": COLORS["edge"],
                    "highlight": "#60a5fa",
                    "hover": "#93c5fd",
                },
                width=2,
                arrows={
                    "to": {
                        "enabled": True,
                        "scaleFactor": 0.8,
                    }
                },
                smooth={
                    "enabled": True,
                    "type": "dynamic",
                },
                font={
                    "color": "#cbd5e1",
                    "size": 12,
                    "face": "Inter, Arial, sans-serif",
                    "background": "#080d18",
                    "strokeWidth": 0,
                },
            )
        )

    return nodes, edges
    