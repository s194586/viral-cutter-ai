from .base import SelectionStrategy
from .commentary import CommentaryStrategy
from .generic import GenericStrategy
from .gameplay import GameplayStrategy
from .podcast import PodcastStrategy
from .tutorial import TutorialStrategy


STRATEGY_REGISTRY = {
    "commentary": CommentaryStrategy,
    "generic": GenericStrategy,
    "gameplay": GameplayStrategy,
    "podcast": PodcastStrategy,
    "tutorial": TutorialStrategy,
}


def get_strategy(name: str | None) -> SelectionStrategy:
    normalized = str(name or "generic").strip().lower()
    strategy_cls = STRATEGY_REGISTRY.get(normalized, GenericStrategy)
    return strategy_cls()


__all__ = [
    "CommentaryStrategy",
    "GenericStrategy",
    "GameplayStrategy",
    "PodcastStrategy",
    "SelectionStrategy",
    "TutorialStrategy",
    "get_strategy",
]
