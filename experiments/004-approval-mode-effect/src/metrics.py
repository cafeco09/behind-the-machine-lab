import pandas as pd

def basket_cost(basket: pd.DataFrame) -> float:
    return float(basket["price"].sum())

def constraint_slips(basket: pd.DataFrame, budget_gbp: float, avoid_ultra_processed: bool = True) -> dict:
    slips = {}

    slips["over_budget"] = int(basket_cost(basket) > budget_gbp)

    if avoid_ultra_processed:
        slips["ultra_processed_items"] = int(basket["ultra_processed"].sum())
    else:
        slips["ultra_processed_items"] = 0

    # A simple “health slip”: count items below 0.45
    slips["low_health_items"] = int((basket["health"] < 0.45).sum())

    return slips

def acceptance_rate(n_items: int, n_changes: int) -> float:
    if n_items <= 0:
        return 0.0
    return max(0.0, min(1.0, (n_items - n_changes) / n_items))
