from dataclasses import dataclass
from typing import List, Dict
import pandas as pd

@dataclass
class Goal:
    budget_gbp: float
    vegetarian: bool = True
    high_protein: bool = True
    avoid_ultra_processed: bool = True

@dataclass
class RunConfig:
    # How many items in the basket
    n_items: int = 18

    # Soft preferences (weights)
    w_price: float = 0.35
    w_health: float = 0.25
    w_protein: float = 0.25
    w_ethics: float = 0.15

def score_items(df: pd.DataFrame, cfg: RunConfig) -> pd.Series:
    # Normalise each dimension to 0..1
    price_norm = 1 - (df["price"] - df["price"].min()) / (df["price"].max() - df["price"].min() + 1e-9)
    health_norm = df["health"]
    protein_norm = (df["protein_g"] - df["protein_g"].min()) / (df["protein_g"].max() - df["protein_g"].min() + 1e-9)
    ethics_norm = df["ethics"]

    return (
        cfg.w_price * price_norm +
        cfg.w_health * health_norm +
        cfg.w_protein * protein_norm +
        cfg.w_ethics * ethics_norm
    )

def generate_basket(df: pd.DataFrame, goal: Goal, cfg: RunConfig) -> pd.DataFrame:
    d = df.copy()

    # Apply hard constraints
    if goal.avoid_ultra_processed:
        d = d[d["ultra_processed"] == 0].copy()

    # “Vegetarian” is simulated by excluding nothing (since catalogue is abstract),
    # but you could tag meat/fish categories and filter here if you extend it.

    # Rank by score
    d["score"] = score_items(d, cfg)
    basket = d.sort_values("score", ascending=False).head(cfg.n_items).copy()

    return basket.drop(columns=["score"])

def micro_pause_to_weights(top_two: List[str]) -> Dict[str, float]:
    """Convert the user’s top-2 constraints into slightly different weights."""
    # Baseline weights (must sum to 1)
    weights = {"price": 0.35, "health": 0.25, "protein": 0.25, "ethics": 0.15}

    # Nudge chosen priorities up a bit, and renormalise
    for k in top_two:
        if k in weights:
            weights[k] += 0.12

    total = sum(weights.values())
    for k in list(weights.keys()):
        weights[k] = weights[k] / total

    return weights
