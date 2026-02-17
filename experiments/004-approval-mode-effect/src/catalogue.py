import numpy as np
import pandas as pd

CATEGORIES = [
    "milk", "bread", "eggs", "fruit", "veg", "snacks", "protein", "cereal",
    "yoghurt", "nuts", "ready_meal", "tofu", "beans"
]

def make_catalogue(n_items: int = 500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    category = rng.choice(CATEGORIES, size=n_items)

    base_price = {
        "milk": 1.40, "bread": 1.30, "eggs": 2.30, "fruit": 2.60, "veg": 2.40,
        "snacks": 2.00, "protein": 4.80, "cereal": 2.90, "yoghurt": 2.20,
        "nuts": 3.20, "ready_meal": 3.80, "tofu": 2.50, "beans": 1.10
    }
    price = np.array([base_price[c] for c in category]) * rng.lognormal(0.0, 0.35, size=n_items)
    price = np.round(price, 2)

    # Health: 0..1 (higher is “better”), loosely category-driven + noise
    cat_health = {
        "milk": 0.65, "bread": 0.60, "eggs": 0.70, "fruit": 0.88, "veg": 0.90,
        "snacks": 0.25, "protein": 0.65, "cereal": 0.55, "yoghurt": 0.62,
        "nuts": 0.75, "ready_meal": 0.35, "tofu": 0.78, "beans": 0.82
    }
    health = np.clip(np.array([cat_health[c] for c in category]) + rng.normal(0, 0.12, n_items), 0, 1)

    # Ethics: 0..1 proxy (higher is “better”), noisy; can be used as a constraint
    ethics = np.clip(rng.beta(3, 3, size=n_items), 0, 1)

    # Protein grams proxy (rough, category-driven)
    cat_protein = {
        "milk": 8, "bread": 7, "eggs": 13, "fruit": 1, "veg": 2,
        "snacks": 4, "protein": 25, "cereal": 8, "yoghurt": 10,
        "nuts": 12, "ready_meal": 14, "tofu": 16, "beans": 9
    }
    protein_g = np.clip(np.array([cat_protein[c] for c in category]) + rng.normal(0, 3, n_items), 0, None)

    df = pd.DataFrame({
        "sku": [f"SKU{str(i).zfill(4)}" for i in range(n_items)],
        "category": category,
        "price": price,
        "health": np.round(health, 3),
        "ethics": np.round(ethics, 3),
        "protein_g": np.round(protein_g, 1),
    })

    # Label some items “ultra_processed” as a simple binary proxy
    ultra_processed = (df["category"].isin(["snacks", "ready_meal"])) & (df["health"] < 0.45)
    df["ultra_processed"] = ultra_processed.astype(int)

    return df
