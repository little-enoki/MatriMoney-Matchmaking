# MatriMoney-Matchmaking 💍
Content-based recommendation system for wedding inspo 👰🏻‍♀️

Give it a **budget** (a dollar amount) and a **style** — `Outdoor spaces`,
`Hotels`, `Vineyards`, or `Restaurants` — and it returns up to **5 San
Francisco venues** that match the style and are priced at or under the
budget, ranked by a simple match score.

This is a scaled-down, personal-project version of the kind of
budget/preference matching used in larger recommendation systems.

## How it works

1. **Data** (`data/sf_venues.json`): San Francisco wedding venues pulled from
   [Zola's wedding venue search](https://www.zola.com/wedding-vendors/wedding-venues),
   filtered to venues in San Francisco and tagged with one or more of the
   four supported styles. See `data/build_dataset.py` for exactly which
   Zola searches the data came from and how it's assembled.
2. **Recommender** (`src/recommender.py`): filters venues to those matching
   the requested style with a listed starting price at or under budget, then
   ranks them with a content-based score that blends:
   - **rating** (50% weight) — how well-reviewed the venue is
   - **budget utilization** (35% weight) — rewards venues that use more of
     the couple's budget without going over it, on the idea that a venue
     priced closer to the budget usually includes more
   - **review volume** (15% weight) — a bit of social proof, log-scaled so
     one venue with hundreds of reviews doesn't dominate
3. **Interfaces**: a Python library function (`recommend()`), a
   context-aware wrapper (`recommend_with_context()`) that can explain thin
   or empty results, and a CLI (`src/cli.py`).

## Quickstart

```bash
git clone <this repo>
cd matrimoney-matching

# Regenerate the dataset (optional -- data/sf_venues.json is already committed)
python3 data/build_dataset.py

# Get recommendations
python3 src/cli.py --budget 5000 --style "Hotels"
python3 src/cli.py --budget 3000 --style "Outdoor spaces"

# Or run it interactively
python3 src/cli.py
```

Example output:

```
San Francisco Hotels venues under $5,000:

  1. Hotel Kabuki -- starts at $5,000 | up to 400 guests
     5.0★ (2 reviews) | match score 0.89
     https://www.zola.com/wedding-vendors/wedding-venues/hotel-kabuki
  2. Rick & Roxy's -- starts at $1,500 | 60-100 guests
     5.0★ (2 reviews) | match score 0.65
  ...
```

Or use it as a library:

```python
from recommender import recommend

results = recommend(budget=5000, style="Hotels")
for r in results:
    print(r["name"], r["price"], r["match_score"])
```

## Running the tests

```bash
python3 -m unittest discover -s tests -v
```

13 tests cover: dataset integrity (every venue is San Francisco, every style
tag is valid), input validation (rejects unknown styles / non-positive
budgets), that results never exceed 5, that every result actually matches
the requested style and budget, that results are sorted by score, and that
edge cases (very low budgets, zero-match styles) degrade gracefully instead
of crashing.

## A real-world data quirk: Vineyards

San Francisco is a dense city with no working vineyards inside its limits,
and Zola's data reflects that: its only vineyard/winery-tagged result for a
"San Francisco" venue search is actually in Fairfield, CA, about an hour
away. Since this project is scoped strictly to San Francisco, that result
was excluded rather than fudged in, which means **`Vineyards` always
returns zero matches for San Francisco, at any budget.** The CLI and library
both handle this as an expected empty result (see
`test_vineyards_has_zero_matches_in_sf_by_design` in the test suite) rather
than an error, and print a clear explanation instead of an empty list. It's
a small, honest example of a real constraint a recommendation system has to
handle: sometimes the inventory for a requested facet just doesn't exist in
the requested region.

## Project structure

```
matrimoney-matching/
├── README.md
├── data/
│   ├── build_dataset.py   # builds sf_venues.json from Zola search data (with provenance notes)
│   └── sf_venues.json     # the venue dataset used by the recommender
├── src/
│   ├── recommender.py     # core scoring + recommendation logic
│   └── cli.py             # command-line interface
└── tests/
    └── test_recommender.py
```

## Data disclaimer

Venue names, prices, capacities, and ratings were captured from Zola's
public wedding-venue search results for San Francisco, CA on 2026-09-17.
Starting prices, availability, and other details change over time — always
confirm directly with a venue (and on Zola) before making decisions. This
project is an independent portfolio piece and is not affiliated with or
endorsed by Zola.
