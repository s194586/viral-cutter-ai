from .base import SelectionStrategy


class CommentaryStrategy(SelectionStrategy):
    def __init__(self) -> None:
        super().__init__(
            name="commentary",
            content_type="commentary",
            description="Favor clear monologue beats, analysis-heavy narration and complete hook-to-payoff commentary arcs.",
            score_weights={
                "heatmap_avg": 0.22,
                "heatmap_peak": 0.08,
                "importance_score": 0.16,
                "speech_density_score": 0.14,
                "emotion_score": 0.06,
                "punchiness_score": 0.06,
                "hook_score": 0.10,
                "payoff_score": 0.10,
                "speaker_turn_score": 0.02,
                "duration_fit_score": 0.06,
                "chaos_score": 0.10,
                "repetition_penalty": 0.10,
            },
            candidate_preferences={
                "prefer_complete_argument": True,
                "prefer_clear_delivery": True,
                "prefer_contextual_setup": True,
            },
            render_hints={
                "crop_mode": "balanced",
                "preserve_screen_content": True,
                "facecam_priority": "secondary",
            },
        )
