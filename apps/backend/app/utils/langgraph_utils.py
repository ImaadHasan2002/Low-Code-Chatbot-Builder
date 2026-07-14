from typing import List, Optional

from langchain_core.documents import Document
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph

from ..core.config import get_settings
from ..services.langchain_service import LangChainService


class ChatbotState(MessagesState):
    """Custom state class for the chatbot, including retrieval context."""

    retrieved_context: Optional[str] = None
    workspace_id: Optional[str] = None


class LangGraphService:
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ):
        settings = get_settings()
        self.model = None
        if settings.OPENAI_API_KEY:
            from langchain_openai import ChatOpenAI

            self.model = ChatOpenAI(
                model=model_name,
                api_key=settings.OPENAI_API_KEY,
                temperature=temperature,
                max_tokens=max_tokens,
            )

        self.langchain_service = LangChainService()

        self.workflow = StateGraph(state_schema=ChatbotState)
        self.workflow.add_node("retrieve_context", self.retrieve_context)
        self.workflow.add_node("model", self.call_model)
        self.workflow.add_edge(START, "retrieve_context")
        self.workflow.add_edge("retrieve_context", "model")

        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    def retrieve_context(self, state: ChatbotState):
        """Retrieve relevant context for the latest human message."""
        messages = state["messages"]

        if not messages or not any(isinstance(msg, HumanMessage) for msg in messages):
            return {"retrieved_context": None}

        last_human_message = next(
            msg for msg in reversed(messages) if isinstance(msg, HumanMessage)
        )
        query = last_human_message.content

        try:
            namespace = state.get("workspace_id")
            if not namespace:
                return {"retrieved_context": None}

            retrieved_docs = self.langchain_service.similarity_search(query, namespace=namespace)
            if retrieved_docs:
                retrieved_context = "\n\n".join(
                    f"Document {i + 1}:\n{doc.page_content}"
                    for i, doc in enumerate(retrieved_docs)
                )
            else:
                retrieved_context = None

            return {"retrieved_context": retrieved_context}
        except Exception as e:
            print(f"Error in retrieval: {str(e)}")
            return {"retrieved_context": None}

    def call_model(self, state: ChatbotState):
        """Generate a response with context awareness."""
        messages: List[BaseMessage] = state["messages"]
        retrieved_context = state.get("retrieved_context")

        if self.model is None:
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "The chatbot is not fully configured yet: no OpenAI API key "
                            "is set on the server. Please add OPENAI_API_KEY to the "
                            "backend environment and restart."
                        )
                    )
                ]
            }

        system_prompt = (
            "You are a helpful assistant. Respond in a friendly and professional tone. "
            "Don't use technical terms like 'context', 'retrieved information' or "
            "'knowledge base'. If the question is unclear, ask a clarifying question. "
            "Use any relevant information provided below to answer the question."
        )

        if retrieved_context:
            system_prompt += f"\n\nContext information:\n{retrieved_context}"
        else:
            system_prompt += (
                "\n\nNo specific context is available. Don't make up information; "
                "politely say you don't have that information if asked about specifics."
            )

        system_message = SystemMessage(content=system_prompt)

        if not messages:
            return {"messages": []}

        try:
            # Filter out any system messages from history; we inject our own.
            history = [m for m in messages if not isinstance(m, SystemMessage)]

            if len(history) > 8:
                summary_message = self._create_summary(history[:-1])
                response = self.model.invoke(
                    [system_message, summary_message, history[-1]]
                )
            else:
                response = self.model.invoke([system_message] + history)
            return {"messages": [response]}
        except Exception as e:
            print(f"Error in call_model: {str(e)}")
            return {
                "messages": [
                    AIMessage(
                        content=(
                            "I apologize, but I encountered an error processing your "
                            "request. Please try again."
                        )
                    )
                ]
            }

    def _create_summary(self, message_history: List[BaseMessage]):
        """Create a summary of past conversation messages."""
        summary_prompt = (
            "Distill the above chat messages into a single summary message. "
            "Include as many specific details as you can."
        )
        return self.model.invoke(message_history + [HumanMessage(content=summary_prompt)])

    def get_workspace_context(self, workspace_id: str, query: str, k: int = 4) -> List[Document]:
        """Get context documents from a specific workspace."""
        try:
            return self.langchain_service.rag_fusion_search(
                query=query, namespace=workspace_id, k=k
            )
        except Exception as e:
            print(f"Error retrieving workspace context: {e}")
            return []

    def invoke_with_workspace(
        self,
        messages: List[BaseMessage],
        workspace_id: Optional[str] = None,
        thread_id: str = "default",
    ):
        """Invoke the graph with a workspace-scoped retrieval namespace."""
        state = {"messages": messages, "workspace_id": workspace_id}
        return self.app.invoke(state, config={"configurable": {"thread_id": thread_id}})
