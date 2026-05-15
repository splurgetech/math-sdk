"""
Sugar Rush 1000–style stepped pay ladder (Stake-published values, × total bet).

Cluster sizes 5–14 use exact columns; size 15+ uses the final column. Mapped 1:1
onto Clash Kronos Cluster pay symbols from low (L3) to high (H1).
"""

# Payouts for cluster sizes 5,6,...,14,15+ (11 entries) per SR1000 tier (× bet).
_SR_ROWS: dict[str, list[float]] = {
    "orange_gummy": [0.20, 0.25, 0.30, 0.40, 0.50, 1.00, 1.50, 2.50, 5.00, 10.00, 20.00],
    "purple_gummy": [0.25, 0.30, 0.40, 0.50, 0.75, 1.25, 2.00, 3.00, 6.00, 12.00, 25.00],
    "red_gummy": [0.30, 0.40, 0.50, 0.75, 1.00, 1.50, 2.50, 3.50, 8.00, 15.00, 30.00],
    "green_candy": [0.40, 0.50, 0.75, 1.00, 1.25, 2.00, 3.00, 5.00, 10.00, 20.00, 40.00],
    "purple_candy": [0.50, 0.75, 1.00, 1.25, 1.50, 3.00, 4.50, 10.00, 20.00, 40.00, 60.00],
    "orange_candy": [0.75, 1.00, 1.25, 1.50, 2.00, 4.00, 6.00, 12.50, 30.00, 60.00, 100.00],
    "pink_candy": [1.00, 1.50, 1.75, 2.00, 2.50, 5.00, 7.50, 15.00, 35.00, 70.00, 150.00],
}

# Low → high: L3 … H1 aligned to SR tiers (seven tiers, seven symbols).
_SYMBOL_TO_SR: list[tuple[str, str]] = [
    ("L3", "orange_gummy"),
    ("L2", "purple_gummy"),
    ("L1", "red_gummy"),
    ("M1", "green_candy"),
    ("M2", "purple_candy"),
    ("H2", "orange_candy"),
    ("H1", "pink_candy"),
]


def build_sugar_rush_style_paytable(scale: float = 1.0) -> dict:
    """Return paytable keys (cluster_size, symbol) with cluster_size in 5..15 (15 = 15+).

    ``scale`` uniformly scales all published ladder values (use ``< 1`` to lower RTP vs
    raw SR1000 multiples under this game's FS / mult rules).
    """
    paytable: dict[tuple[int, str], float] = {}
    for game_sym, sr_key in _SYMBOL_TO_SR:
        row = _SR_ROWS[sr_key]
        for i, cluster_size in enumerate(range(5, 15)):
            paytable[(cluster_size, game_sym)] = round(row[i] * scale, 6)
        paytable[(15, game_sym)] = round(row[10] * scale, 6)
    return paytable
