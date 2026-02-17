import time
from agent_styles import Goal, RunConfig, generate_basket, micro_pause_to_weights
from catalogue import make_catalogue
from metrics import basket_cost, constraint_slips, acceptance_rate

def print_basket(title, basket):
    print(f"\n=== {title} ===")
    print(basket[["sku", "category", "price", "health", "protein_g", "ethics", "ultra_processed"]].to_string(index=False))
    print(f"Total cost: £{basket_cost(basket):.2f}")

def ask_int(prompt: str, default: int) -> int:
    s = input(f"{prompt} (default {default}): ").strip()
    if not s:
        return default
    try:
        return int(s)
    except ValueError:
        return default

def ask_float(prompt: str, default: float) -> float:
    s = input(f"{prompt} (default {default}): ").strip()
    if not s:
        return default
    try:
        return float(s)
    except ValueError:
        return default

def main():
    print("Approval Mode Effect — A/B experiment (synthetic retail basket)\n")

    budget = ask_float("Budget cap in GBP", 25.0)
    n_items = ask_int("Target number of items in basket", 18)

    goal = Goal(budget_gbp=budget)
    df = make_catalogue()

    # --- A: Control ---
    cfg_a = RunConfig(n_items=n_items)
    start_a = time.time()
    basket_a = generate_basket(df, goal, cfg_a)
    end_a = time.time()

    print_basket("A (Control) — immediate basket", basket_a)

    changes_a = ask_int("How many items would you change before checkout (A)?", 4)
    secs_a = ask_int("Rough time-to-checkout in seconds (A)?", int(end_a - start_a) + 60)

    # --- B: Treatment (micro-pause) ---
    print("\nB (Treatment) — micro-pause: choose your top 2 constraints for today.")
    print("Options: price, health, protein, ethics")
    top1 = input("Top 1: ").strip().lower() or "price"
    top2 = input("Top 2: ").strip().lower() or "health"

    w = micro_pause_to_weights([top1, top2])
    cfg_b = RunConfig(
        n_items=n_items,
        w_price=w["price"],
        w_health=w["health"],
        w_protein=w["protein"],
        w_ethics=w["ethics"],
    )

    start_b = time.time()
    basket_b = generate_basket(df, goal, cfg_b)
    end_b = time.time()

    print_basket("B (Treatment) — basket after micro-pause", basket_b)

    changes_b = ask_int("How many items would you change before checkout (B)?", 3)
    secs_b = ask_int("Rough time-to-checkout in seconds (B)?", int(end_b - start_b) + 65)

    # --- Metrics ---
    slips_a = constraint_slips(basket_a, budget_gbp=budget)
    slips_b = constraint_slips(basket_b, budget_gbp=budget)

    ar_a = acceptance_rate(n_items, changes_a)
    ar_b = acceptance_rate(n_items, changes_b)

    print("\n=== Results (directional) ===")
    print(f"Acceptance rate A: {ar_a:.2f} | B: {ar_b:.2f}")
    print(f"Cost A: £{basket_cost(basket_a):.2f} | B: £{basket_cost(basket_b):.2f}")
    print(f"Time A: {secs_a}s | B: {secs_b}s")
    print(f"Slips A: {slips_a}")
    print(f"Slips B: {slips_b}")

    print("\nInterpretation:")
    print("- If B reduces slips with similar time, the micro-pause improved review quality.")
    print("- If acceptance rate stays very high in both, you’re in approval mode either way.")
    print("- Repeat on a different day / different goal to reduce warm-up effects.\n")

if __name__ == "__main__":
    main()
