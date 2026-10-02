"""
Command-line interface for MatriMoney Matching.

Usage:
    python3 src/cli.py --budget 5000 --style "Hotels"
    python3 src/cli.py --budget 3000 --style "Outdoor spaces"

Run with no arguments for an interactive prompt.
"""

import argparse
import sys

from recommender import VALID_STYLES, recommend_with_context


def prompt_for_inputs() -> tuple[float, str]:
    while True:
        raw_budget = input("What's your budget for the venue? (number, e.g. 5000): ").strip()
        try:
            budget = float(raw_budget.replace("$", "").replace(",", ""))
            if budget > 0:
                break
        except ValueError:
            pass
        print("Please enter a positive number.")

    print("\nStyles available:")
    for i, s in enumerate(VALID_STYLES, 1):
        print(f"  {i}. {s}")
    while True:
        raw_style = input("Pick a style (name or number): ").strip()
        if raw_style.isdigit() and 1 <= int(raw_style) <= len(VALID_STYLES):
            return budget, VALID_STYLES[int(raw_style) - 1]
        for s in VALID_STYLES:
            if raw_style.lower() == s.lower():
                return budget, s
        print(f"Please enter one of: {', '.join(VALID_STYLES)}")


def print_results(context: dict) -> None:
    budget = context["budget"]
    style = context["style"]
    results = context["results"]

    print(f"\nSan Francisco {style} venues under ${budget:,.0f}:\n")

    if not results:
        if context["style_total_in_sf"] == 0:
            print(
                f"  No San Francisco venues are tagged '{style}' at all "
                "(see data/build_dataset.py for why -- some styles genuinely "
                "have zero matches within SF city limits, like Vineyards)."
            )
        else:
            print(
                f"  No '{style}' venues in San Francisco were found at or under "
                f"${budget:,.0f}. There are {context['style_total_in_sf']} "
                f"'{style}' venues in SF total -- try a higher budget."
            )
        return

    for i, v in enumerate(results, 1):
        cap = ""
        if v["capacity_min"] or v["capacity_max"]:
            lo = v["capacity_min"] or "?"
            hi = v["capacity_max"] or "?"
            cap = f" | up to {hi} guests" if not v["capacity_min"] else f" | {lo}-{hi} guests"
        rating = f"{v['rating']:.1f}★ ({v['review_count']} reviews)" if v["review_count"] else "no reviews yet"
        print(f"  {i}. {v['name']} -- starts at ${v['price']:,}{cap}")
        print(f"     {rating} | match score {v['match_score']:.2f}")
        print(f"     {v['url']}")

    if len(results) < 5 and context["matches_under_budget"] < 5:
        print(
            f"\n  (Only {context['matches_under_budget']} '{style}' venue(s) in San "
            f"Francisco fall at or under ${budget:,.0f}.)"
        )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="MatriMoney Matching -- SF wedding venue recommender")
    parser.add_argument("--budget", type=float, help="Your budget in dollars, e.g. 5000")
    parser.add_argument("--style", choices=VALID_STYLES, help="Venue style")
    args = parser.parse_args(argv)

    if args.budget is not None and args.style is not None:
        budget, style = args.budget, args.style
    else:
        budget, style = prompt_for_inputs()

    context = recommend_with_context(budget, style)
    print_results(context)
    return 0


if __name__ == "__main__":
    sys.exit(main())
