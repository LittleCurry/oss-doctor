"""Core result types shared by checks and reporters."""

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class Result:
    """The outcome of one repository health check."""

    check_id: str
    title: str
    status: str
    message: str
    recommendation: str
    weight: int

    @property
    def points(self) -> float:
        if self.status == "pass":
            return float(self.weight)
        if self.status == "warn":
            return self.weight / 2
        return 0.0


@dataclass(frozen=True)
class Report:
    """A complete, serializable repository health report."""

    path: Path
    results: List[Result]

    @property
    def score(self) -> int:
        total = sum(result.weight for result in self.results)
        if not total:
            return 0
        return round(100 * sum(result.points for result in self.results) / total)

    @property
    def grade(self) -> str:
        if self.score >= 90:
            return "A"
        if self.score >= 80:
            return "B"
        if self.score >= 70:
            return "C"
        if self.score >= 60:
            return "D"
        return "F"

    @property
    def counts(self) -> Dict[str, int]:
        return {
            status: sum(result.status == status for result in self.results)
            for status in ("pass", "warn", "fail")
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "path": str(self.path),
            "score": self.score,
            "grade": self.grade,
            "counts": self.counts,
            "results": [asdict(result) for result in self.results],
        }
