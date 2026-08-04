from sqlalchemy.orm import Session

from models.story import Story, StoryNode


class MockStoryGenerator:

    @classmethod
    def generate_story(cls, db: Session, session_id: str, theme: str = "fantasy") -> Story:
        story_db = Story(title=f"Mock story: {theme}", session_id=session_id)
        db.add(story_db)
        db.flush()

        root_node = StoryNode(
            story_id=story_db.id,
            content=f"This is a mock adventure about {theme}.",
            is_root=True,
            is_ending=False,
            is_winning_ending=False,
            options=[]
        )
        db.add(root_node)
        db.flush()

        first_choice_node = StoryNode(
            story_id=story_db.id,
            content="You hear a noise in the forest and can either investigate or run away.",
            is_root=False,
            is_ending=False,
            is_winning_ending=False,
            options=[]
        )
        db.add(first_choice_node)
        db.flush()

        second_choice_node = StoryNode(
            story_id=story_db.id,
            content="You run to safety, but the mystery only grows.",
            is_root=False,
            is_ending=True,
            is_winning_ending=False,
            options=[]
        )
        db.add(second_choice_node)
        db.flush()

        root_node.options = [
            {"text": "Investigate the noise", "node_id": first_choice_node.id},
            {"text": "Run away", "node_id": second_choice_node.id}
        ]
        db.flush()

        first_choice_node.options = [
            {"text": "Approach carefully", "node_id": second_choice_node.id},
            {"text": "Shout to announce yourself", "node_id": second_choice_node.id}
        ]
        db.flush()

        db.commit()
        return story_db
