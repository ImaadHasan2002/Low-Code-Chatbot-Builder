from typing import List, Optional, Set

from bson import ObjectId
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage

from ..core.config import get_settings
from ..models.advanced_config import AdvancedConfig
from ..models.conversation import Conversation
from ..utils.langgraph_utils import LangGraphService

settings = get_settings()

DEFAULT_SYSTEM_PROMPT = """You are a helpful assistant that only answers based on provided context information.

CRITICAL INSTRUCTIONS:
1. If the user asks about something not covered in the context, respond with: "I'm sorry, but I don't have information about that in my knowledge base."
2. Never make up information or guess when unsure - be honest about your limitations.
3. If you have partial information but aren't fully confident, express your uncertainty clearly with phrases like "Based on the limited information available..." or "I'm not entirely certain, but..."
4. Do not reference external sources, research, or datasets that aren't explicitly mentioned in the context.
5. Stick to factual information from the provided context only.
"""


class ChatbotService:
    def __init__(self, workspace_id: Optional[str] = None):
        self.workspace_id = workspace_id
        self._config: Optional[AdvancedConfig] = None
        self.langgraph = LangGraphService()
        self.default_blocked_words: Set[str] = set()
        self.default_system_prompt = DEFAULT_SYSTEM_PROMPT

    async def load_workspace_config(self):
        """Load per-workspace AdvancedConfig from DB and reconfigure the LLM."""
        if not self.workspace_id:
            return
        try:
            self._config = await AdvancedConfig.find_one(
                AdvancedConfig.workspace_id == ObjectId(self.workspace_id)
            )
        except Exception as e:
            print(f"Could not load workspace config: {e}")
            return

        if self._config:
            model_name = self._config.llm_model or "gpt-4o-mini"
            self.langgraph = LangGraphService(
                model_name=model_name,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
            )
            if self._config.system_prompt:
                self.default_system_prompt = self._config.system_prompt
            if self._config.block_words:
                self.default_blocked_words = set(self._config.block_words)

    def _create_system_prompt(
        self,
        custom_prompt: Optional[str] = None,
        context: Optional[List[Document]] = None,
        blocked_words: Optional[Set[str]] = None,
    ) -> str:
        """Create a system prompt with optional customization, context, and blocked words."""
        prompt = custom_prompt if custom_prompt else self.default_system_prompt

        if blocked_words:
            blocked_list = ", ".join(f'"{word}"' for word in blocked_words)
            prompt += (
                f"\n\nYou must not discuss or mention these topics: {blocked_list}. "
                "If asked about them, politely decline by saying: "
                "'I'm sorry, but I'm not programmed to discuss this topic.'"
            )

        if context:
            prompt += "\n\nContext information (USE ONLY THIS TO ANSWER QUESTIONS):\n"
            for i, doc in enumerate(context):
                prompt += f"\n--- Document {i + 1} ---\n{doc.page_content}\n"

        return prompt

    async def generate_response(
        self,
        query: str,
        blocked_words: Optional[Set[str]] = None,
        custom_prompt: Optional[str] = None,
        thread_id: Optional[str] = None,
    ) -> str:
        """Generate a response via the LangGraph workflow (retrieval included)."""
        if blocked_words is None:
            blocked_words = self.default_blocked_words

        system_content = self._create_system_prompt(custom_prompt, None, blocked_words)

        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=query),
        ]

        response = self.langgraph.invoke_with_workspace(
            messages,
            workspace_id=str(self.workspace_id) if self.workspace_id else None,
            thread_id=thread_id or str(self.workspace_id or "default"),
        )
        return response["messages"][-1].content

    async def generate_response_with_retrieval(
        self,
        query: str,
        blocked_words: Optional[Set[str]] = None,
        custom_prompt: Optional[str] = None,
        thread_id: Optional[str] = None,
        save: bool = False,
        user_id: Optional[str] = None,
    ) -> str:
        """Generate a retrieval-augmented response. Retrieval happens inside
        the LangGraph workflow using the workspace namespace."""
        response = await self.generate_response(
            query,
            blocked_words=blocked_words,
            custom_prompt=custom_prompt,
            thread_id=thread_id,
        )

        if save and self.workspace_id and user_id:
            try:
                conversation = Conversation(
                    workspace_id=ObjectId(self.workspace_id),
                    user_id=ObjectId(user_id),
                    query=query,
                    response=response,
                )
                await conversation.insert()
            except Exception as e:
                print(f"Could not save conversation (non-fatal): {e}")

        return response

    async def update_feedback(self, conversation_id: str, feedback: str) -> bool:
        """Record feedback on a conversation."""
        conversation = await Conversation.get(ObjectId(conversation_id))
        if not conversation:
            return False
        conversation.feedback = feedback
        await conversation.save()
        return True
