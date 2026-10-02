"""
MatriMoney Matching
--------------------
A small content-based recommendation engine for San Francisco wedding
venues, built as a scaled-down showcase of the kind of budget/preference
matching used in systems like Aetna/CVS Smart Care's recommendation engine.

Given a couple's budget (a number, in dollars) and a preferred venue style
("Outdoor spaces", "Hotels", "Vineyards", or "Restaurants"), this module
returns up to 5 San Francisco venues that are:
  1. tagged with the requested style, and
  2. priced at or below the given budget,
ranked by a simple content-based match score (see `score_venue`).

Data source: data/sf_venues.json, built from Zola's San Francisco wedding
venue listings (https://www.zola.com/wedding-vendors/wedding-venues) --
see data/build_dataset.py for provenance.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from typing import Optional

VALID_STYLES = ("Outdoor spaces", "Hotels", "Vineyards", "Restaurants")

DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sf_venues.json"
)


@dataclass
class Venue:
    id: str
    name: str
    city: str
    state: str
    price: Optional[int]
    capacity_min: Optional[int]
    capacity_max: Optional[int]
    rating: float
    review_count: int
    indoor_outdoor: list = field(default_factory=list)
    service_level: Optional[str] = None
    styles: list = field(default_factory=list)
    url: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "Venue":
        return cls(
            id=d["id"],
            name=d["name"],
            city=d["city"],
            state=d["state"],
            price=d.get("price"),
            capacity_min=d.get("capacity_min"),
            capacity_max=d.get("capacity_max"),
            rating=d.get("rating") or 0,
            review_count=d.get("review_count") or 0,
            indoor_outdoor=d.get("indoor_outdoor") or [],
            service_level=d.get("service_level"),
            styles=d.get("styles") or [],
            url=d.get("url", ""),
        )


def load_venues(data_path: str = DEFAULT_DATA_PATH) -> list[Venue]:
    """Load the San Francisco venue dataset from disk."""
    with open(data_path) as f:
        payload = json.load(f)
    return [Venue.from_dict(v) for v in payload["venues"]]


def score_venue(venue: Venue, budget: float) -> float:
    """
    Content-based match score in [0, 1], higher is better.

    Blends three signals a couple actually cares about:
      - rating (0-5 stars)              weight 0.5
      - review volume (social proof)    weight 0.15   (log-scaled, caps out around 50 reviews)
      - budget utilization              weight 0.35   (rewards venues that use more of the
                                                          couple's budget, on the theory that a
                                                          $9,000 venue on a $10,000 budget
                                                          usually offers more than a $2,000 one,
                                                          while never exceeding the budget)
    """
    rating_component = (venue.rating or 0) / 5.0

    review_component = min(math.log1p(venue.review_count) / math.log1p(50), 1.0)

    if venue.price is None or budget <= 0:
        budget_component = 0.0
    else:
        budget_component = min(venue.price / budget, 1.0)

    return round(
        0.5 * rating_component + 0.15 * review_component + 0.35 * budget_component, 4
    )


def recommend(
    budget: float,
    style: str,
    top_n: int = 5,
    data_path: str = DEFAULT_DATA_PATH,
    venues: Optional[list[Venue]] = None,
) -> list[dict]:
    """
    Return up to `top_n` San Francisco venues matching `style` and priced at
    or under `budget`, ranked best-match first.

    Raises ValueError for an unrecognized style or a non-positive budget.
    """
    if style not in VALID_STYLES:
        raise ValueError(f"style must be one of {VALID_STYLES!r}, got {style!r}")
    if budget is None or budget <= 0:
        raise ValueError("budget must be a positive number")

    pool = venues if venues is not None else load_venues(data_path)

    candidates = [
        v for v in pool if style in v.styles and v.price is not None and v.price <= budget
    ]
    candidates.sort(key=lambda v: score_venue(v, budget), reverse=True)

    results = []
    for v in candidates[:top_n]:
        results.append(
            {
                "name": v.name,
                "price": v.price,
                "rating": v.rating,
                "review_count": v.review_count,
                "capacity_min": v.capacity_min,
                "capacity_max": v.capacity_max,
                "styles": v.styles,
                "match_score": score_venue(v, budget),
                "url": v.url,
            }
        )
    return results


def recommend_with_context(budget: float, style: str, top_n: int = 5) -> dict:
    """
    Like `recommend`, but also reports how many total venues carry the
    requested style (regardless of budget) so a caller/UI can explain a thin
    or empty result set (e.g. "Vineyards" has zero San Francisco matches at
    any budget -- see data/build_dataset.py for why).
    """
    all_venues = load_venues()
    style_total = sum(1 for v in all_venues if style in v.styles)
    under_budget = recommend(budget, style, top_n=top_n, venues=all_venues)
    return {
        "budget": budget,
        "style": style,
        "style_total_in_sf": style_total,
        "matches_under_budget": len(
            [v for v in all_venues if style in v.styles and v.price is not None and v.price <= budget]
        ),
        "results": under_budget,
    }
