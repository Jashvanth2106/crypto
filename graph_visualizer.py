"""
CryptoShield - Custom Investigation Graph

Premium SVG-based blockchain flow visualization.
No external graph rendering library required.
"""

import json
import math


# =========================================================
# COLORS
# =========================================================

BG = "#050816"
GRID = "#101a31"

BLUE = "#3b82f6"
RED = "#ff365f"
PURPLE = "#a855f7"
ORANGE = "#f59e0b"

TEXT = "#e5e7eb"
MUTED = "#64748b"


def short_address(address: str) -> str:
    if len(address) <= 14:
        return address

    return f"{address[:6]}...{address[-4:]}"


def build_premium_graph(
    transactions: list[dict],
    suspect_address: str,
) -> str:
    """
    Build a custom interactive SVG investigation graph.
    """

    suspect_address = suspect_address.lower()

    # -----------------------------------------------------
    # Collect wallets
    # -----------------------------------------------------

    wallets = set()
    flows = []

    for tx in transactions:

        sender = str(tx.get("from") or "").lower()
        receiver = str(tx.get("to") or "").lower()

        if not sender or not receiver:
            continue

        if sender == receiver:
            continue

        try:
            value_wei = int(tx.get("value", "0") or 0)
        except (ValueError, TypeError):
            value_wei = 0

        value_eth = value_wei / 10**18

        wallets.add(sender)
        wallets.add(receiver)

        flows.append(
            {
                "from": sender,
                "to": receiver,
                "value": value_eth,
            }
        )

    if not wallets:
        return """
        <div style="
            height:720px;
            display:flex;
            align-items:center;
            justify-content:center;
            background:#050816;
            color:#94a3b8;
            font-family:Inter,Arial,sans-serif;
        ">
            No transaction flow available.
        </div>
        """

    # -----------------------------------------------------
    # Build graph relationships
    # -----------------------------------------------------

    connections = {}

    for flow in flows:

        a = flow["from"]
        b = flow["to"]

        connections.setdefault(a, set()).add(b)
        connections.setdefault(b, set()).add(a)

    # -----------------------------------------------------
    # Layout
    #
    # Suspect = center
    # Everything else arranged around it.
    # -----------------------------------------------------

    center_x = 600
    center_y = 350

    positions = {}

    positions[suspect_address] = (
        center_x,
        center_y,
    )

    others = [
        wallet
        for wallet in wallets
        if wallet != suspect_address
    ]

    # Put connected wallets closer to center.
    others.sort(
        key=lambda wallet: (
            -len(connections.get(wallet, set())),
            wallet,
        )
    )

    radius_base = 190

    for index, wallet in enumerate(others):

        total = max(len(others), 1)

        angle = (
            (2 * math.pi * index / total)
            - math.pi / 2
        )

        ring = index // 8

        radius = radius_base + ring * 130

        x = center_x + math.cos(angle) * radius
        y = center_y + math.sin(angle) * radius

        positions[wallet] = (
            x,
            y,
        )

    # -----------------------------------------------------
    # Nodes
    # -----------------------------------------------------

    node_html = ""

    for wallet, (x, y) in positions.items():

        is_suspect = wallet == suspect_address

        if is_suspect:

            color = RED
            radius = 46
            label = "SUSPECT WALLET"
            role = "Investigated wallet"

        else:

            color = BLUE
            radius = 30
            label = short_address(wallet)
            role = "Blockchain wallet"

        node_html += f"""
        <g
            class="wallet-node"
            data-address="{wallet}"
            transform="translate({x:.1f},{y:.1f})"
        >

            <circle
                class="node-glow"
                r="{radius + 16}"
                fill="{color}"
                opacity="0.10"
            />

            <circle
                class="node-glow-2"
                r="{radius + 8}"
                fill="{color}"
                opacity="0.15"
            />

            <circle
                class="node-circle"
                r="{radius}"
                fill="#0b1224"
                stroke="{color}"
                stroke-width="3"
            />

            <circle
                r="{max(radius - 8, 5)}"
                fill="{color}"
                opacity="0.16"
            />

            <text
                class="node-label"
                y="{radius + 25}"
                text-anchor="middle"
            >
                {label}
            </text>

            <text
                class="node-role"
                y="{radius + 42}"
                text-anchor="middle"
            >
                {role}
            </text>

        </g>
        """

    # -----------------------------------------------------
    # Edges
    # -----------------------------------------------------

    edge_html = ""

    for index, flow in enumerate(flows):

        sender = flow["from"]
        receiver = flow["to"]
        value = flow["value"]

        if sender not in positions:
            continue

        if receiver not in positions:
            continue

        x1, y1 = positions[sender]
        x2, y2 = positions[receiver]

        # Curved midpoint.
        mx = (x1 + x2) / 2
        my = (y1 + y2) / 2

        dx = x2 - x1
        dy = y2 - y1

        distance = max(
            math.sqrt(dx * dx + dy * dy),
            1,
        )

        offset = min(
            70,
            distance * 0.18,
        )

        cx = mx - (dy / distance) * offset
        cy = my + (dx / distance) * offset

        path = (
            f"M {x1:.1f} {y1:.1f} "
            f"Q {cx:.1f} {cy:.1f} "
            f"{x2:.1f} {y2:.1f}"
        )

        edge_html += f"""
        <g class="flow-line">

            <path
                d="{path}"
                class="flow-path"
            />

            <text
                x="{cx:.1f}"
                y="{cy - 8:.1f}"
                class="flow-label"
                text-anchor="middle"
            >
                {value:.4f} ETH
            </text>

        </g>
        """

    # -----------------------------------------------------
    # HTML
    # -----------------------------------------------------

    return f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<style>

* {{
    box-sizing: border-box;
}}

html,
body {{
    margin: 0;
    padding: 0;
    background: {BG};
    overflow: hidden;
    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}}

.graph-shell {{
    width: 100%;
    height: 720px;
    position: relative;
    overflow: hidden;

    background:
        radial-gradient(
            circle at 50% 45%,
            rgba(59,130,246,0.08),
            transparent 35%
        ),
        radial-gradient(
            circle at 20% 20%,
            rgba(168,85,247,0.05),
            transparent 30%
        ),
        {BG};

    border:
        1px solid rgba(148,163,184,0.14);

    border-radius: 20px;

    box-shadow:
        inset 0 0 80px rgba(0,0,0,0.35),
        0 20px 60px rgba(0,0,0,0.35);
}}

.graph-header {{
    position: absolute;
    top: 22px;
    left: 26px;
    right: 26px;
    z-index: 20;

    display: flex;
    justify-content: space-between;
    align-items: center;

    pointer-events: none;
}}

.graph-title {{
    color: #f8fafc;
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

.graph-subtitle {{
    color: {MUTED};
    font-size: 11px;
    margin-top: 4px;
}}

.live {{
    display: flex;
    align-items: center;
    gap: 8px;

    padding: 8px 12px;

    border-radius: 999px;

    background: rgba(34,197,94,0.08);
    border: 1px solid rgba(34,197,94,0.18);

    color: #86efac;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.08em;
}}

.live-dot {{
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #22c55e;

    box-shadow:
        0 0 12px rgba(34,197,94,0.9);
}}

svg {{
    width: 100%;
    height: 100%;
    cursor: grab;
}}

svg:active {{
    cursor: grabbing;
}}

.grid {{
    stroke: {GRID};
    stroke-width: 1;
    opacity: 0.7;
}}

.flow-path {{
    fill: none;
    stroke: #334155;
    stroke-width: 2.5;

    marker-end: url(#arrow);

    transition:
        stroke 0.2s ease,
        stroke-width 0.2s ease;
}}

.flow-line:hover .flow-path {{
    stroke: #60a5fa;
    stroke-width: 4;
}}

.flow-label {{
    fill: #cbd5e1;
    font-size: 11px;
    font-weight: 700;

    paint-order: stroke;
    stroke: {BG};
    stroke-width: 5px;
    stroke-linejoin: round;
}}

.wallet-node {{
    cursor: pointer;

    transition:
        transform 0.2s ease;
}}

.node-circle {{
    transition:
        stroke 0.2s ease,
        fill 0.2s ease;
}}

.wallet-node:hover .node-circle {{
    stroke: #ffffff;
    fill: #101a31;
}}

.wallet-node:hover .node-glow {{
    opacity: 0.25;
}}

.node-label {{
    fill: {TEXT};
    font-size: 12px;
    font-weight: 800;
}}

.node-role {{
    fill: {MUTED};
    font-size: 9px;
    letter-spacing: 0.04em;
}}

.legend {{
    position: absolute;

    left: 24px;
    bottom: 22px;

    display: flex;
    gap: 18px;

    padding: 10px 14px;

    background:
        rgba(5,8,22,0.78);

    backdrop-filter: blur(12px);

    border:
        1px solid rgba(148,163,184,0.13);

    border-radius: 12px;
}}

.legend-item {{
    display: flex;
    align-items: center;
    gap: 7px;

    color: #94a3b8;

    font-size: 10px;
    font-weight: 700;
}}

.legend-dot {{
    width: 8px;
    height: 8px;
    border-radius: 50%;
}}

.info-panel {{
    position: absolute;

    right: 22px;
    bottom: 22px;

    min-width: 210px;

    padding: 14px;

    background:
        rgba(8,13,24,0.90);

    backdrop-filter: blur(18px);

    border:
        1px solid rgba(96,165,250,0.16);

    border-radius: 14px;

    box-shadow:
        0 15px 40px rgba(0,0,0,0.35);

    opacity: 0;
    transform: translateY(8px);

    transition:
        opacity 0.2s ease,
        transform 0.2s ease;

    pointer-events: none;
}}

.info-panel.active {{
    opacity: 1;
    transform: translateY(0);
}}

.info-title {{
    color: #f8fafc;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.08em;
}}

.info-address {{
    color: #60a5fa;
    font-size: 10px;
    margin-top: 6px;
    word-break: break-all;
}}

</style>

</head>

<body>

<div class="graph-shell">

    <div class="graph-header">

        <div>

            <div class="graph-title">
                Fund Flow Intelligence
            </div>

            <div class="graph-subtitle">
                Interactive blockchain transaction topology
            </div>

        </div>

        <div class="live">

            <span class="live-dot"></span>

            LIVE ANALYSIS

        </div>

    </div>


    <svg
        id="graph"
        viewBox="0 0 1200 720"
        preserveAspectRatio="xMidYMid meet"
    >

        <defs>

            <pattern
                id="grid"
                width="40"
                height="40"
                patternUnits="userSpaceOnUse"
            >

                <path
                    d="M 40 0 L 0 0 0 40"
                    fill="none"
                    class="grid"
                />

            </pattern>


            <marker
                id="arrow"
                markerWidth="8"
                markerHeight="8"
                refX="7"
                refY="3"
                orient="auto"
            >

                <path
                    d="M0,0 L0,6 L7,3 z"
                    fill="#60a5fa"
                />

            </marker>

        </defs>


        <rect
            width="1200"
            height="720"
            fill="url(#grid)"
        />


        <g id="viewport">

            {edge_html}

            {node_html}

        </g>

    </svg>


    <div class="legend">

        <div class="legend-item">
            <span
                class="legend-dot"
                style="background:{RED}"
            ></span>
            Suspect
        </div>

        <div class="legend-item">
            <span
                class="legend-dot"
                style="background:{BLUE}"
            ></span>
            Wallet
        </div>

        <div class="legend-item">
            <span
                class="legend-dot"
                style="background:{ORANGE}"
            ></span>
            Suspicious
        </div>

        <div class="legend-item">
            <span
                class="legend-dot"
                style="background:{PURPLE}"
            ></span>
            VASP
        </div>

    </div>


    <div
        id="info"
        class="info-panel"
    >

        <div class="info-title">
            WALLET INTELLIGENCE
        </div>

        <div
            id="infoAddress"
            class="info-address"
        ></div>

    </div>

</div>


<script>

const svg = document.getElementById("graph");
const viewport = document.getElementById("viewport");

let scale = 1;
let offsetX = 0;
let offsetY = 0;

let dragging = false;
let startX = 0;
let startY = 0;


function updateTransform() {{

    viewport.setAttribute(
        "transform",
        `translate(${{offsetX}} ${{offsetY}})
         scale(${{scale}})`
    );

}}


svg.addEventListener(
    "wheel",
    function(event) {{

        event.preventDefault();

        const direction =
            event.deltaY > 0
            ? 0.9
            : 1.1;

        scale *= direction;

        scale = Math.max(
            0.55,
            Math.min(2.5, scale)
        );

        updateTransform();

    }},
    {{ passive: false }}
);


svg.addEventListener(
    "mousedown",
    function(event) {{

        if (
            event.target.closest(
                ".wallet-node"
            )
        ) {{
            return;
        }}

        dragging = true;

        startX = event.clientX - offsetX;
        startY = event.clientY - offsetY;

    }}
);


window.addEventListener(
    "mousemove",
    function(event) {{

        if (!dragging) return;

        offsetX =
            event.clientX - startX;

        offsetY =
            event.clientY - startY;

        updateTransform();

    }}
);


window.addEventListener(
    "mouseup",
    function() {{
        dragging = false;
    }}
);


document
    .querySelectorAll(".wallet-node")
    .forEach(
        function(node) {{

            node.addEventListener(
                "click",
                function(event) {{

                    event.stopPropagation();

                    const address =
                        node.dataset.address;

                    document
                        .getElementById(
                            "infoAddress"
                        )
                        .textContent = address;

                    document
                        .getElementById("info")
                        .classList.add("active");

                }}
            );

        }}
    );

</script>

</body>

</html>
"""
