from core.config import settings
from core.mock_story_generator import MockStoryGenerator
from core.story_generator import StoryGenerator


class StoryFactory:
    PROVIDERS = {
        "mock": MockStoryGenerator,
        "openai": StoryGenerator,
    }

    @classmethod
    def generate_story(cls, db, session_id: str, theme: str = "fantasy"):
        provider_name = settings.STORY_PROVIDER
        provider = cls.PROVIDERS.get(provider_name)
        if provider is None:
            raise ValueError(
                f"Unsupported story provider '{provider_name}'. "
                f"Supported providers: {', '.join(cls.PROVIDERS)}"
            )
        return provider.generate_story(db, session_id, theme)
