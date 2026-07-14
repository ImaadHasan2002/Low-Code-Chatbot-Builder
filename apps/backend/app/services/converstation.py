# NOTE: filename kept as "converstation.py" (sic) for backwards compatibility.
# Prefer importing from app.services.conversation_service going forward.
from ..core.config import get_settings
from ..models.conversation import Conversation


class ConversationService:
    def __init__(self):
        self.settings = get_settings()

    async def create_conversation(self, conversation: Conversation):
        await conversation.insert()
        return str(conversation.id)
