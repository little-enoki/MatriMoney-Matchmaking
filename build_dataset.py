"""
Builds data/sf_venues.json from venue records collected from Zola's San
Francisco wedding-venue search results (https://www.zola.com/wedding-vendors/
wedding-venues), filtered to the four style categories this project supports:
Outdoor spaces, Hotels, Vineyards, Restaurants.

Each record below was captured from Zola's own search-results payload
(the same JSON that powers zola.com's venue cards) for these searches,
scoped to San Francisco, CA on 2026-09-17:
  - .../san-francisco-ca--wedding-venues--hotels-inns-resorts   (style: Hotels)
  - .../san-francisco-ca--wedding-venues--vineyards-wineries    (style: Vineyards)
  - .../san-francisco-ca--wedding-venues--restaurants-breweries (style: Restaurants)
  - .../san-francisco-ca--wedding-venues--outdoor-space         (style: Outdoor spaces)

A venue can legitimately carry more than one style tag (e.g. a hotel with an
outdoor terrace). Only venues whose city is exactly "San Francisco" are kept,
per the project's scope -- this is also why "Vineyards" ends up nearly empty:
Zola's only vineyard/winery-tagged result for the San Francisco search is
actually in Fairfield, CA (there are no working vineyards within SF city
limits), so it is excluded and the Vineyards category is left with zero real
matches. The recommender handles that gracefully rather than faking data.

Run: python3 build_dataset.py   (writes ../data/sf_venues.json... actually
writes sf_venues.json alongside this script, i.e. data/sf_venues.json)
"""

import json
import os

STYLE_HOTELS = "Hotels"
STYLE_VINEYARDS = "Vineyards"
STYLE_RESTAURANTS = "Restaurants"
STYLE_OUTDOOR = "Outdoor spaces"

# name -> raw record. price is Zola's "startingPriceCents" converted to whole
# dollars (None if Zola doesn't publish a starting price for that venue).
# capacity is (min, max) guest count, either side may be None.
RAW = {
    # ---- Hotels, Inns, Resorts (city == San Francisco only) ----
    "hotels": [
        {"name": "Hotel Kabuki", "slug": "hotel-kabuki", "price": 5000, "cap": (None, 400), "rating": 5.0, "reviews": 2, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "The Westin St. Francis - San Francisco", "slug": "the-westin-st-francis-san-francisco", "price": 15000, "cap": (None, 750), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Beacon Grand, A Union Square Hotel", "slug": "beacon-grand-a-union-square-hotel", "price": None, "cap": (5, 200), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Hotel Via", "slug": "hotel-via", "price": 15000, "cap": (50, 125), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["outdoor"], "service_level": "select services"},
        {"name": "Rick & Roxy's", "slug": "rick-roxy-s", "price": 1500, "cap": (60, 100), "rating": 5.0, "reviews": 2, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Argonaut Hotel", "slug": "argonaut-hotel", "price": 15000, "cap": (10, 350), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Chambers eat + drink", "slug": "chambers-eat-drink", "price": 15000, "cap": (25, 200), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "covered-outdoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Hotel Adagio", "slug": "hotel-adagio", "price": 5000, "cap": (None, 80), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "The Marker San Francisco", "slug": "the-marker-san-francisco", "price": 125, "cap": (10, 150), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Hotel Nikko San Francisco", "slug": "hotel-nikko-san-francisco", "price": 5000, "cap": (None, 550), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "The Clift Royal Sonesta Hotel San Francisco", "slug": "the-clift-royal-sonesta-hotel-san-francisco", "price": 4500, "cap": (100, 150), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Marines' Memorial Club", "slug": "marines-memorial-club", "price": 1750, "cap": (10, 270), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Four Seasons San Francisco", "slug": "four-seasons-san-francisco", "price": 35000, "cap": (None, 450), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Hotel Emblem San Francisco", "slug": "hotel-emblem-san-francisco", "price": None, "cap": (None, 150), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Hyatt Regency San Francisco Downtown Soma", "slug": "hyatt-regency-san-francisco-downtown-soma", "price": 15000, "cap": (50, 500), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Hyatt Regency Downtown SOMA", "slug": "hyatt-regency-downtown-soma", "price": None, "cap": (1, 900), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "The St. Regis San Francisco", "slug": "the-st-regis-san-francisco", "price": 30000, "cap": (None, 250), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "covered-outdoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "The City Club Of San Francisco", "slug": "the-city-club-of-san-francisco", "price": 12000, "cap": (25, 220), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Hotel VIA Rooftop", "slug": "hotel-via-rooftop", "price": 7000, "cap": (50, 100), "rating": 0, "reviews": 0, "indoor_outdoor": ["covered-outdoor", "outdoor"], "service_level": "select services"},
    ],
    # ---- Restaurants, Breweries (city == San Francisco only) ----
    "restaurants": [
        {"name": "Marigold Event Space", "slug": "marigold-event-space", "price": 1600, "cap": (None, 50), "rating": 5.0, "reviews": 2, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Sam's Grill and Seafood restaurant", "slug": "sams-grill-and-seafood-restaurant", "price": 120, "cap": (1, 40), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "Queen's Louisiana Po-boy Cafe", "slug": "queens-louisiana-po-boy-cafe", "price": 4000, "cap": (30, 100), "rating": 5.0, "reviews": 2, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Rick & Roxy's", "slug": "rick-roxy-s", "price": 1500, "cap": (60, 100), "rating": 5.0, "reviews": 2, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "B Star", "slug": "b-star", "price": 1100, "cap": (5, 35), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor", "covered-outdoor"], "service_level": "all-inclusive"},
        {"name": "Presidio Golf Course & Clubhouse", "slug": "presidio-golf-course-clubhouse", "price": 5000, "cap": (40, 230), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor", "outdoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "Al-Masri Egyptian Restaurant", "slug": "al-masri-egyptian-restaurant--2", "price": 1000, "cap": (20, 60), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor"], "service_level": None},
        {"name": "Whitechapel", "slug": "whitechapel", "price": 5000, "cap": (35, 115), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Chambers eat + drink", "slug": "chambers-eat-drink", "price": 15000, "cap": (25, 200), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "covered-outdoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Birdsong", "slug": "birdsong", "price": None, "cap": (1, 45), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Mission Bowling Club", "slug": "mission-bowling-club", "price": None, "cap": (None, 75), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "620 Jones", "slug": "620-jones", "price": 1000, "cap": (None, 1400), "rating": 0, "reviews": 0, "indoor_outdoor": ["outdoor", "indoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "The Marker San Francisco", "slug": "the-marker-san-francisco", "price": 125, "cap": (10, 150), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Che Fico", "slug": "che-fico", "price": 30000, "cap": (None, 150), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Marines' Memorial Club", "slug": "marines-memorial-club", "price": 1750, "cap": (10, 270), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Del Popolo", "slug": "del-popolo", "price": 2500, "cap": (None, 90), "rating": 0, "reviews": 0, "indoor_outdoor": [], "service_level": "select services"},
        {"name": "Starlite", "slug": "starlite", "price": 10000, "cap": (40, 90), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "111 Minna Gallery", "slug": "111-minna-gallery", "price": 7680, "cap": (None, 75), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Tequila Mockingbird", "slug": "tequila-mockingbird", "price": 1500, "cap": (None, None), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Yerba Buena Bar", "slug": "yerba-buena-bar", "price": 1500, "cap": (None, None), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": None},
        {"name": "Natoma Cabana", "slug": "natoma-cabana", "price": 500, "cap": (2, 70), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "Temple San Francisco", "slug": "temple-san-francisco", "price": 8000, "cap": (30, 100), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Empress by Boon", "slug": "empress-by-boon", "price": 4000, "cap": (None, 250), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Macondray", "slug": "macondray", "price": 1500, "cap": (None, None), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "High Horse", "slug": "high-horse", "price": 500, "cap": (2, 80), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "select services"},
        {"name": "Palm House", "slug": "palm-house--3", "price": 12500, "cap": (14, 30), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "Monroe", "slug": "monroe--2", "price": None, "cap": (None, 250), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Hilda and Jesse", "slug": "hilda-and-jesse", "price": 3500, "cap": (1, 50), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor"], "service_level": "all-inclusive"},
        {"name": "Harborview Restaurant & Bar", "slug": "harborview-restaurant-bar", "price": 5000, "cap": (None, 300), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
    ],
    # ---- Outdoor spaces (venue-setting facet, city == San Francisco only) ----
    "outdoor": [
        {"name": "Log Cabin at the Presidio by Wedgewood Weddings", "slug": "presidio-log-cabin-by-wedgewood-weddings", "price": 11865, "cap": (2, 150), "rating": 5.0, "reviews": 9, "indoor_outdoor": ["outdoor", "indoor"], "service_level": "all-inclusive"},
        {"name": "Hotel Via", "slug": "hotel-via", "price": 15000, "cap": (50, 125), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["outdoor"], "service_level": "select services"},
        {"name": "Bay Lights Charters", "slug": "bay-lights-charters", "price": 3800, "cap": (2, 49), "rating": 5.0, "reviews": 100, "indoor_outdoor": ["outdoor"], "service_level": "all-inclusive"},
        {"name": "Plant Connection SF", "slug": "plant-connection-sf", "price": 1200, "cap": (None, 96), "rating": 5.0, "reviews": 4, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "Exploratorium", "slug": "exploratorium", "price": 11900, "cap": (50, 500), "rating": 5.0, "reviews": 3, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "raw space"},
        {"name": "City Cruises San Francisco", "slug": "city-cruises-san-francisco", "price": 3000, "cap": (None, 645), "rating": 3.8, "reviews": 71, "indoor_outdoor": ["outdoor", "indoor"], "service_level": "all-inclusive"},
        {"name": "Queen's Louisiana Po-boy Cafe", "slug": "queens-louisiana-po-boy-cafe", "price": 4000, "cap": (30, 100), "rating": 5.0, "reviews": 2, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "The Pearl", "slug": "the-pearl", "price": None, "cap": (75, 220), "rating": 4.45, "reviews": 20, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "Argonaut Hotel", "slug": "argonaut-hotel", "price": 15000, "cap": (10, 350), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Golden Gate Club at the Presidio", "slug": "presidio-golden-gate-club-by-wedgewood-weddings", "price": 15365, "cap": (2, 300), "rating": 5.0, "reviews": 9, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Presidio Golf Course & Clubhouse", "slug": "presidio-golf-course-clubhouse", "price": 5000, "cap": (40, 230), "rating": 5.0, "reviews": 1, "indoor_outdoor": ["indoor", "outdoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "Chambers eat + drink", "slug": "chambers-eat-drink", "price": 15000, "cap": (25, 200), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "covered-outdoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "620 Jones", "slug": "620-jones", "price": 1000, "cap": (None, 1400), "rating": 0, "reviews": 0, "indoor_outdoor": ["outdoor", "indoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "Hotel Adagio", "slug": "hotel-adagio", "price": 5000, "cap": (None, 80), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "City View At Metreon", "slug": "city-view-at-metreon", "price": None, "cap": (None, 800), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "raw space"},
        {"name": "Four Seasons San Francisco", "slug": "four-seasons-san-francisco", "price": 35000, "cap": (None, 450), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "The St. Regis San Francisco", "slug": "the-st-regis-san-francisco", "price": 30000, "cap": (None, 250), "rating": 0, "reviews": 0, "indoor_outdoor": ["covered-outdoor", "indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Hotel VIA Rooftop", "slug": "hotel-via-rooftop", "price": 7000, "cap": (50, 100), "rating": 0, "reviews": 0, "indoor_outdoor": ["covered-outdoor", "outdoor"], "service_level": "select services"},
        {"name": "Palm House", "slug": "palm-house--3", "price": 12500, "cap": (14, 30), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "Monroe", "slug": "monroe--2", "price": None, "cap": (None, 250), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Harborview Restaurant & Bar", "slug": "harborview-restaurant-bar", "price": 5000, "cap": (None, 300), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Coqueta", "slug": "coqueta", "price": 15000, "cap": (1, 75), "rating": 0, "reviews": 0, "indoor_outdoor": ["covered-outdoor", "indoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "The Ramp", "slug": "the-ramp", "price": 25000, "cap": (20, 350), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "The Commonwealth Club Of California", "slug": "the-commonwealth-club-of-california", "price": None, "cap": (80, 200), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor", "covered-outdoor"], "service_level": "select services"},
        {"name": "Grumpy's Pub & Pizza", "slug": "grumpy-s-pub-pizza", "price": 4000, "cap": (15, 80), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
        {"name": "Presido Chapel at the Presidio", "slug": "presido-chapel-by-wedgewood-weddings", "price": None, "cap": (2, 150), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "covered-outdoor", "outdoor"], "service_level": "all-inclusive"},
        {"name": "Skyline Events SF", "slug": "skyline-events-sf", "price": None, "cap": (None, 300), "rating": 0, "reviews": 0, "indoor_outdoor": ["indoor", "outdoor"], "service_level": "select services"},
    ],
    # ---- Vineyards, Wineries ----
    # Zola's ONLY vineyard/winery-tagged result for the San Francisco search
    # is Suisun Valley Inn, which is actually located in Fairfield, CA (not
    # San Francisco). Since this project is scoped to San Francisco only,
    # and there are no vineyards within SF city limits, this category is
    # intentionally left empty. See README for how the recommender handles
    # a style with zero matches.
    "vineyards": [],
}

STYLE_SOURCE_MAP = {
    "hotels": STYLE_HOTELS,
    "restaurants": STYLE_RESTAURANTS,
    "outdoor": STYLE_OUTDOOR,
    "vineyards": STYLE_VINEYARDS,
}

SOURCE_URLS = {
    "hotels": "https://www.zola.com/wedding-vendors/search/san-francisco-ca--wedding-venues--hotels-inns-resorts",
    "restaurants": "https://www.zola.com/wedding-vendors/search/san-francisco-ca--wedding-venues--restaurants-breweries",
    "outdoor": "https://www.zola.com/wedding-vendors/search/san-francisco-ca--wedding-venues--outdoor-space",
    "vineyards": "https://www.zola.com/wedding-vendors/search/san-francisco-ca--wedding-venues--vineyards-wineries",
}


def build():
    venues = {}
    for source_key, records in RAW.items():
        style = STYLE_SOURCE_MAP[source_key]
        for rec in records:
            slug = rec["slug"]
            if slug not in venues:
                venues[slug] = {
                    "id": slug,
                    "name": rec["name"],
                    "city": "San Francisco",
                    "state": "CA",
                    "price": rec["price"],
                    "capacity_min": rec["cap"][0],
                    "capacity_max": rec["cap"][1],
                    "rating": rec["rating"],
                    "review_count": rec["reviews"],
                    "indoor_outdoor": rec["indoor_outdoor"],
                    "service_level": rec["service_level"],
                    "styles": [],
                    "url": f"https://www.zola.com/wedding-vendors/wedding-venues/{slug}",
                    "source": [],
                }
            v = venues[slug]
            if style not in v["styles"]:
                v["styles"].append(style)
            if SOURCE_URLS[source_key] not in v["source"]:
                v["source"].append(SOURCE_URLS[source_key])
            # Prefer a non-null price if one source lacks it
            if v["price"] is None and rec["price"] is not None:
                v["price"] = rec["price"]

    out = sorted(venues.values(), key=lambda v: v["name"])

    out_path = os.path.join(os.path.dirname(__file__), "sf_venues.json")
    with open(out_path, "w") as f:
        json.dump(
            {
                "location": "San Francisco, CA",
                "styles": [STYLE_OUTDOOR, STYLE_HOTELS, STYLE_VINEYARDS, STYLE_RESTAURANTS],
                "source": "https://www.zola.com/wedding-vendors/wedding-venues",
                "collected": "2026-09-17",
                "venue_count": len(out),
                "venues": out,
            },
            f,
            indent=2,
        )
    print(f"Wrote {len(out)} venues to {out_path}")
    for style in (STYLE_OUTDOOR, STYLE_HOTELS, STYLE_VINEYARDS, STYLE_RESTAURANTS):
        n = sum(1 for v in out if style in v["styles"])
        priced = sum(1 for v in out if style in v["styles"] and v["price"] is not None)
        print(f"  {style}: {n} venues ({priced} with a listed starting price)")


if __name__ == "__main__":
    build()
