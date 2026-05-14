from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from layout import get_layout_profile


@dataclass
class SelectionStrategy:
    name: str
    content_type: str
    description: str
    score_weights: dict[str, float]
    candidate_preferences: dict[str, Any] = field(default_factory=dict)
    render_hints: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        layout_profile = get_layout_profile(self.content_type)
        merged_render_hints = {
            **layout_profile.to_render_hints(),
            **dict(self.render_hints),
        }
        return {
            "name": self.name,
            "content_type": self.content_type,
            "description": self.description,
            "score_weights": dict(self.score_weights),
            "candidate_preferences": dict(self.candidate_preferences),
            "render_hints": merged_render_hints,
            "layout": layout_profile.to_dict(),
        }
