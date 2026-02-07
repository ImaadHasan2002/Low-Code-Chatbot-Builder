from app.models.conversation import Conversation
from app.core.config import get_settings


class ConversationService:
    def __init__(self):
        self.settings = get_settings()

    async def create_conversation(self, conversation: Conversation):
        response = await Conversation.insert_one(conversation)
        print("response", response)
        return response._id
