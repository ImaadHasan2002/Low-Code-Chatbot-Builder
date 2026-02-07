from langchain_core.messages import HumanMessage, RemoveMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI
from ..core.config import get_settings
from ..services.langchain_service import LangChainService
from typing import List, Dict, Any, Optional, TypedDict
from langchain_core.documents import Document
from fastapi import Depends
from ..core.security import get_current_workspace
from langchain_core.messages import BaseMessage

# Define our custom state class
class ChatbotState(MessagesState):
    """Custom state class for chatbot that includes context information"""
    messages: List[BaseMessage]
    retrieved_context: Optional[str] = None

class LangGraphService:
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.2, max_tokens: int = 1000):
        self.graph = None
        self.workflow = StateGraph(state_schema=ChatbotState)
        settings = get_settings()

        self.model = ChatOpenAI(
            model=model_name,
            api_key=settings.OPENAI_API_KEY,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Initialize LangChain service for retrieval
        self.langchain_service = LangChainService()

        # Add nodes to workflow
        self.workflow.add_node("retrieve_context", self.retrieve_context)
        self.workflow.add_node("process_context", self.process_context)
        self.workflow.add_node("model", self.call_model)
        
        # Define workflow edges with retrieval
        self.workflow.add_edge(START, "retrieve_context")
        self.workflow.add_edge("retrieve_context", "process_context")
        self.workflow.add_edge("process_context", "model")
        
        self.memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=self.memory)

    def retrieve_context(self, state: ChatbotState, workspace_id: Optional[str] = None):
        """
        Retrieve relevant context using RAG Fusion.
        
        Args:
            state: Current message state
            workspace_id: Optional workspace ID for namespace
        """
        messages = state["messages"]
        
        # Skip retrieval if no human message is present
        if not messages or not any(isinstance(msg, HumanMessage) for msg in messages):
            return {"messages": messages, "retrieved_context": None}
        
        # Get the last human message
        last_human_message = next(msg for msg in reversed(messages) 
                                if isinstance(msg, HumanMessage))
        query = last_human_message.content
        
        try:
            # Use the provided workspace_id or default
            namespace = workspace_id or "67b1c1d1c91e325f5eae3f95"
            
            # Perform RAG Fusion search
            retrieved_docs = self.langchain_service.similarity_search(query)
            # Format retrieved context
            if retrieved_docs:
                retrieved_context = "\n\n".join([
                    f"Document {i+1}:\n{doc.page_content}" 
                    for i, doc in enumerate(retrieved_docs)
                ])
            else:
                retrieved_context = "No relevant information found in the knowledge base."
            
            # Don't overwrite messages, just return both
            return {
                "messages": messages + [SystemMessage(content=retrieved_context)],
                "retrieved_context": retrieved_context,
            }
        except Exception as e:
            # Log error and continue without context
            print(f"Error in retrieval: {str(e)}")
            return {"messages": messages, "retrieved_context": None}

    def process_context(self, state: ChatbotState):
        """Process and extract context from messages and retrieval."""
        messages = state["messages"]
        retrieved_context = state["retrieved_context"]

        print(f"Retrieved context in process_context: {retrieved_context}")
        context = None
        
        # Check for system message with context
        if len(messages) > 0 and isinstance(messages[0], SystemMessage):
            context = messages[0].content
            messages = messages[1:]
        
        # Combine with retrieved context if available
        if retrieved_context:
            if context:
                context += f"\n\nRetrieved Information:\n{retrieved_context}"
            else:
                context = f"Retrieved Information:\n{retrieved_context}"
        print(f"Context: {context}")
        return {
            "messages": messages,
            "retrieved_context": retrieved_context,
        }

    def call_model(self, state: ChatbotState):
        """Generate response with context awareness."""
        messages = state["messages"]
        retrieved_context = state["retrieved_context"]

        system_prompt = "You are a helpful assistant. Respond in a friendly and professional tone. Don't use technical terms like 'context' or 'retrieved information' or 'knowledge base'. If unclear then ask clarifying question. Use any relevant information in the System Message to answer the question. Use the retrieved context to answer the question if it is relevant. Also you can use system message to answer the question if it is relevant."
        
        # Add context information
        if retrieved_context and len(retrieved_context) > 0:
            system_prompt += f"\n\nContext information:\n{retrieved_context}"
        else:
            system_prompt += "\n\nNo specific context is provided. Don't make up information. Just Politely deny\n\nkeep professional and friendly tone, don't use technical terms like 'context' or 'retrieved information' or 'knowledge base'\n\n if unclear then ask clarifying question\n\nuse any relevant information in the System Message to answer the question"
        
        system_message = SystemMessage(content=system_prompt)
        
        # Safely handle message history
        if not messages:
            return {"messages": [system_message]}
        
        message_history = messages[:-1]
        last_human_message = messages[-1]

        try:
            if len(message_history) >= 4:
                # Create summary and generate response
                summary_message = self._create_summary(message_history)
                response = self.model.invoke(
                    messages=[
                        system_message,
                        summary_message,
                        HumanMessage(content=last_human_message.content if isinstance(last_human_message, HumanMessage) else str(last_human_message))
                    ],
                    config={"configurable": {"thread_id": "4"}}
                )
                
                # Clean up old messages and return new state
                delete_messages = [RemoveMessage(id=msg.id) for msg in messages if hasattr(msg, 'id')]
                return {"messages": [summary_message, last_human_message, response] + delete_messages}
            else:
                # Handle normal conversation flow
                response = self.model.invoke([system_message] + messages, config={"configurable": {"thread_id": "4"}})
                return {"messages": [response]}
            
        except Exception as e:
            print(f"Error in call_model: {str(e)}")
            # Return a graceful error message
            error_message = AIMessage(content="I apologize, but I encountered an error processing your request. Please try again.")
            return {"messages": [error_message]}

    def _create_summary(self, message_history):
        """Create a summary of past conversation messages."""
        summary_prompt = (
            "Distill the above chat messages into a single summary message. "
            "Include as many specific details as you can."
        )
        return self.model.invoke(message_history + [HumanMessage(content=summary_prompt)])
        
    def get_workspace_context(self, workspace_id: str, query: str, k: int = 4) -> List[Document]:
        """
        Get context documents from a specific workspace.
        
        Args:
            workspace_id: Workspace to search in
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents
        """
        try:
            # Use RAG Fusion for better retrieval
            docs = self.langchain_service.rag_fusion_search(
                query=query,
                namespace=workspace_id,
                k=k
            )
            return docs
        except Exception as e:
            print(f"Error retrieving workspace context: {e}")
            return []

    def invoke_with_workspace(self, 
                             messages: List, 
                             workspace_id: str = None,
                             thread_id: str = "default"):
        """
        Invoke LangGraph with a specific workspace context.
        
        Args:
            messages: List of messages
            workspace_id: Workspace ID for retrieval
            thread_id: Thread ID for conversation isolation
            
        Returns:
            LangGraph response
        """
        # Add workspace metadata to state
        state = {
            "messages": messages,
            "workspace_id": workspace_id
        }
        
        # Invoke LangGraph with workspace context
        response = self.app.invoke(
            state, 
            config={"configurable": {"thread_id": thread_id}}
        )
        
        return response