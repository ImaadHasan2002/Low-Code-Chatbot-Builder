from typing import List, Optional, Set
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from fastapi import Depends
from bson import ObjectId
from ..services.langchain_service import LangChainService
from ..models.conversation import Conversation
from ..models.advanced_config import AdvancedConfig
from ..core.config import get_settings
from ..utils.langgraph_utils import LangGraphService
from langchain_core.documents import Document
from ..core.security import get_current_user, get_current_workspace
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
        # Defaults used until workspace config is loaded
        self.llm = ChatOpenAI(
            temperature=0.2,
            model_name="gpt-4o-mini",
            api_key=settings.OPENAI_API_KEY
        )
        self.langchain = LangChainService()
        self.langgraph = LangGraphService()
        self.default_blocked_words = set()
        self.default_system_prompt = DEFAULT_SYSTEM_PROMPT

    async def load_workspace_config(self):
        """Load per-workspace AdvancedConfig from DB and reconfigure LLM."""
        if not self.workspace_id:
            return
        self._config = await AdvancedConfig.find_one(
            AdvancedConfig.workspace_id == ObjectId(self.workspace_id)
        )
        if self._config:
            # Reconfigure LLM with workspace settings
            model_name = self._config.llm_model or "gpt-4o-mini"
            self.llm = ChatOpenAI(
                temperature=self._config.temperature,
                model_name=model_name,
                api_key=settings.OPENAI_API_KEY,
                max_tokens=self._config.max_tokens,
            )
            self.langgraph = LangGraphService(
                model_name=model_name,
                temperature=self._config.temperature,
                max_tokens=self._config.max_tokens,
            )
            if self._config.system_prompt:
                self.default_system_prompt = self._config.system_prompt
            if self._config.block_words:
                self.default_blocked_words = set(self._config.block_words)
        
    def _create_system_prompt(self, custom_prompt: Optional[str] = None,
                             context: Optional[List[Document]] = None, 
                             blocked_words: Optional[Set[str]] = None) -> str:
        """Create a system prompt with optional customization, context, and blocked words."""
        # Use custom prompt if provided, otherwise use default
        prompt = custom_prompt if custom_prompt else self.default_system_prompt

        # Add blocked words/topics if provided
        if blocked_words and len(blocked_words) > 0:
            blocked_list = ", ".join(f'"{word}"' for word in blocked_words)
            prompt += f"\n\nYou must not discuss or mention these topics: {blocked_list}. If asked about them, politely decline by saying: 'I'm sorry, but I'm not programmed to discuss this topic.'"
        
        # Add context information
        if context and len(context) > 0:
            prompt += "\n\nContext information (USE ONLY THIS TO ANSWER QUESTIONS):\n"
            for i, doc in enumerate(context):
                prompt += f"\n--- Document {i+1} ---\n{doc.page_content}\n"
        else:
            prompt += "\n\nNo specific context is provided. Don't make up information. Just Politely deny"
            
        return prompt

    async def generate_response(self, query: str, 
                               context: Optional[List[Document]] = None, 
                               blocked_words: Optional[Set[str]] = None,
                               custom_prompt: Optional[str] = None) -> str:
        """Generate response using LangGraph with configurable system prompt and anti-hallucination controls."""
        try:
            # Use default blocked words if none provided
            if blocked_words is None:
                blocked_words = self.default_blocked_words
                
            # Create system message with custom or default prompt
            system_content = self._create_system_prompt(custom_prompt, context, blocked_words)
            
            # Prepare messages
            messages = [
                SystemMessage(content=system_content),
                HumanMessage(content=query)
            ]

            response = self.langgraph.app.invoke({"messages": messages}, config={"configurable": {"thread_id": "4"}})
            return response["messages"][-1].content

        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")

    async def generate_response_with_retrieval(self, query: str, 
                                              blocked_words: Optional[Set[str]] = None,
                                              custom_prompt: Optional[str] = None, 
                                              use_rag_fusion: bool = True,
                                              user_id = Depends(get_current_user), 
                                              workspace_id = Depends(get_current_workspace)) -> str:
        """
        Generate response with retrieval-augmented generation using configurable retrieval method.
        
        Args:
            query: User query
            blocked_words: Set of words/topics to avoid
            custom_prompt: Optional custom system prompt
            use_rag_fusion: Whether to use RAG Fusion (True) or standard retrieval (False)
            user_id: Current user ID (from dependency)
            workspace_id: Current workspace ID (from dependency)
            
        Returns:
            Generated response based on retrieved context
        """
        try:
            # Retrieve relevant documents using either RAG Fusion or standard similarity search
            # if use_rag_fusion:
            #     print(f"Using RAG Fusion search for query: {query}")
            #     context = self.langchain.rag_fusion_search(query, namespace=workspace_id)
            # else:
            #     print(f"Using standard similarity search for query: {query}")
            #     context = self.langchain.similarity_search(query, namespace=workspace_id)
                
            # # If no context found, make sure the model knows to apologize
            # if not context:
            #     context = [Document(page_content="No relevant information found in the knowledge base.")]
                
            # Generate response with context, blocked words, and optional custom prompt
            response = await self.generate_response(query)
            
            # Save conversation (optional)
            # conversation = Conversation(
            #     workspace_id=workspace_id,
            #     user_id=user_id,
            #     query=query,
            #     response=response,
            # )
            # await self._save_conversation(conversation)
            
            return response
        
        except Exception as e:
            raise Exception(f"Error in retrieval-augmented response: {str(e)}")
        
        # TODO: refactor to use langraph
    async def generate_response_with_langgraph(self, query: str,
                                              blocked_words: Optional[Set[str]] = None,
                                              custom_prompt: Optional[str] = None,
                                              user_id = Depends(get_current_user), 
                                              workspace_id = Depends(get_current_workspace)) -> str:
        """
        Generate response using the LangGraph workflow which has integrated RAG Fusion.
        
        This method uses the multi-step orchestrated workflow defined in LangGraphService
        which includes retrieval, context processing, and response generation.
        """
        try:
            # Prepare initial system message if needed
            system_content = ""
            
            # Add blocked words/topics if provided
            if blocked_words and len(blocked_words) > 0:
                blocked_list = ", ".join(f'"{word}"' for word in blocked_words)
                system_content = f"You must not discuss or mention these topics: {blocked_list}. If asked about them, politely decline."
            
            # Add custom prompt if provided
            if custom_prompt:
                system_content = f"{custom_prompt}\n\n{system_content}" if system_content else custom_prompt
                
            # Prepare messages
            messages = []
            if system_content:
                messages.append(SystemMessage(content=system_content))
                
            messages.append(HumanMessage(content=query))

            # Use LangGraph workflow which has integrated RAG Fusion retrieval
            response = self.langgraph.app.invoke({"messages": messages}, config={"configurable": {"thread_id": "5"}})
            return response["messages"][-1].content
            
        except Exception as e:
            raise Exception(f"Error in LangGraph response: {str(e)}")
        
    async def update_workspace_settings(self, workspace_id: str, blocked_words: Set[str] = None):
        """Update workspace settings including blocked words."""
        try:
            if blocked_words is not None:
                # Store blocked words in database for the specific workspace
                collection = self._get_collection("workspace_settings")
                await collection.update_one(
                    {"workspace_id": workspace_id},
                    {"$set": {"blocked_words": list(blocked_words)}},
                    upsert=True
                )
            return True
        except Exception as e:
            raise Exception(f"Error updating workspace settings: {str(e)}")
            
    async def get_workspace_blocked_words(self, workspace_id: str) -> Set[str]:
        """Get blocked words for a specific workspace."""
        try:
            collection = self._get_collection("workspace_settings")
            settings = await collection.find_one({"workspace_id": workspace_id})
            return set(settings.get("blocked_words", [])) if settings else set()
        except Exception as e:
            return set()
        
    async def _save_conversation(self, conversation: Conversation):
        """Save conversation to database."""
        collection = self._get_collection()
        await collection.insert_one(conversation.model_dump(by_alias=True))

    def _get_collection(self, collection_name="conversations"):
        """Get MongoDB collection."""
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        db = client[settings.DATABASE_NAME]
        return db[collection_name]

# # Block specific words/topics
# blocked_words = {"politics", "religion", "controversy"}
# response = await chatbot.generate_response_with_retrieval(
#     query="Tell me about your features", 
#     blocked_words=blocked_words
# )