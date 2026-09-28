"""Ranking for the internal docs search. Called with the candidate pages for a query."""
from dataclasses import dataclass
from datetime import date


@dataclass
class Page:
    path: str
    title: str
    text_score: float  # BM25 score from the index, higher is better
    updated: date
    views_30d: int


def rank(pages: list[Page]) -> list[Page]:
    return sorted(pages, key=lambda p: (p.text_score, p.views_30d), reverse=True)
