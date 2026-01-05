import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from src.models.data_models import ConversationContext, ConversationTurn
from src.config.settings import settings


class ConversationService:
    """
    Service class for managing conversation contexts including creation, retrieval,
    updating, and expiration of conversations.
    """

    def __init__(self):
        """
        Initialize the ConversationService with an in-memory store for conversations.
        In a production environment, this would use a database or other persistent storage.
        """
        self._conversations: Dict[str, ConversationContext] = {}
        self._cleanup_task = None

    async def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        initial_query: str = None,
        initial_response: str = None
    ) -> ConversationContext:
        """
        Create a new conversation

        Args:
            conversation_id: Optional conversation ID. If not provided, generates a new one.
            initial_query: Optional initial query to add as the first turn
            initial_response: Optional initial response to add as the first turn

        Returns:
            Created ConversationContext
        """
        conv_id = conversation_id or str(uuid.uuid4())

        # Create the first turn if initial query/response are provided
        turns = []
        if initial_query and initial_response:
            first_turn = ConversationTurn(
                turn_id=str(uuid.uuid4()),
                user_query=initial_query,
                system_response=initial_response,
                timestamp=datetime.now()
            )
            turns.append(first_turn)

        # Create the conversation context
        conversation = ConversationContext(
            conversation_id=conv_id,
            turns=turns,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            is_active=True
        )

        # Store the conversation
        self._conversations[conv_id] = conversation

        return conversation

    async def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        Retrieve a conversation by ID

        Args:
            conversation_id: The ID of the conversation to retrieve

        Returns:
            ConversationContext if found, None otherwise
        """
        conversation = self._conversations.get(conversation_id)

        # Check if conversation exists and is not expired
        if conversation and self._is_conversation_expired(conversation):
            await self._expire_conversation(conversation_id)
            return None

        return conversation

    async def add_turn(
        self,
        conversation_id: str,
        user_query: str,
        system_response: str,
        context_summary: Optional[str] = None
    ) -> Optional[ConversationContext]:
        """
        Add a turn to an existing conversation

        Args:
            conversation_id: The ID of the conversation to add the turn to
            user_query: The user's query
            system_response: The system's response
            context_summary: Optional summary of the context for this turn

        Returns:
            Updated ConversationContext if successful, None if conversation not found
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None

        # Check if we need to trim the conversation to stay within limits
        if len(conversation.turns) >= settings.max_conversation_turns:
            # Remove oldest turns to stay within the limit
            excess = len(conversation.turns) - settings.max_conversation_turns + 1
            conversation.turns = conversation.turns[excess:]

        # Create and add the new turn
        new_turn = ConversationTurn(
            turn_id=str(uuid.uuid4()),
            user_query=user_query,
            system_response=system_response,
            timestamp=datetime.now(),
            context_summary=context_summary
        )
        conversation.turns.append(new_turn)
        conversation.last_activity = datetime.now()

        # Update the stored conversation
        self._conversations[conversation_id] = conversation

        return conversation

    async def generate_context_summary(self, conversation_id: str) -> Optional[str]:
        """
        Generate a summary of the conversation context

        Args:
            conversation_id: The ID of the conversation to summarize

        Returns:
            Summary string of the conversation context, or None if conversation not found
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation or not conversation.turns:
            return None

        # Create a simple summary of the conversation
        summary_parts = []
        for turn in conversation.turns[-3:]:  # Summarize last 3 turns for brevity
            summary_parts.append(f"Q: {turn.user_query[:50]}..." if len(turn.user_query) > 50 else f"Q: {turn.user_query}")
            summary_parts.append(f"A: {turn.system_response[:50]}..." if len(turn.system_response) > 50 else f"A: {turn.system_response}")

        return " | ".join(summary_parts)

    async def get_recent_context(self, conversation_id: str, num_turns: int = 5) -> Optional[List[Dict[str, str]]]:
        """
        Get the most recent turns from a conversation as context for the LLM

        Args:
            conversation_id: The ID of the conversation
            num_turns: Number of recent turns to retrieve

        Returns:
            List of dictionaries containing user queries and system responses,
            or None if conversation not found
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None

        # Get the most recent turns
        recent_turns = conversation.turns[-num_turns:]
        context = []
        for turn in recent_turns:
            context.append({
                "user_query": turn.user_query,
                "system_response": turn.system_response
            })

        return context

    async def update_conversation_metadata(
        self,
        conversation_id: str,
        metadata: Dict
    ) -> bool:
        """
        Update metadata for a conversation

        Args:
            conversation_id: The ID of the conversation to update
            metadata: The metadata to update

        Returns:
            True if successful, False if conversation not found
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False

        # Merge the new metadata with existing metadata
        if conversation.metadata:
            conversation.metadata.update(metadata)
        else:
            conversation.metadata = metadata

        # Update the stored conversation
        self._conversations[conversation_id] = conversation

        return True

    async def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation

        Args:
            conversation_id: The ID of the conversation to delete

        Returns:
            True if successful, False if conversation not found
        """
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
            return True
        return False

    async def list_active_conversations(self) -> List[ConversationContext]:
        """
        List all active conversations

        Returns:
            List of active ConversationContext objects
        """
        active_conversations = []
        for conversation in self._conversations.values():
            if not self._is_conversation_expired(conversation):
                active_conversations.append(conversation)
            else:
                # Clean up expired conversations
                await self._expire_conversation(conversation.conversation_id)

        return active_conversations

    async def cleanup_expired_conversations(self) -> int:
        """
        Remove all expired conversations from memory

        Returns:
            Number of conversations removed
        """
        expired_ids = []
        for conv_id, conversation in self._conversations.items():
            if self._is_conversation_expired(conversation):
                expired_ids.append(conv_id)

        for conv_id in expired_ids:
            del self._conversations[conv_id]

        return len(expired_ids)

    def _is_conversation_expired(self, conversation: ConversationContext) -> bool:
        """
        Check if a conversation has expired based on the configured expiry time

        Args:
            conversation: The conversation to check

        Returns:
            True if expired, False otherwise
        """
        expiry_time = timedelta(hours=settings.conversation_expiry_hours)
        time_since_last_activity = datetime.now() - conversation.last_activity
        return time_since_last_activity > expiry_time

    async def _expire_conversation(self, conversation_id: str) -> bool:
        """
        Mark a conversation as expired and remove it from memory

        Args:
            conversation_id: The ID of the conversation to expire

        Returns:
            True if successful, False if conversation not found
        """
        return await self.delete_conversation(conversation_id)

    async def get_conversation_summary(self, conversation_id: str) -> Optional[Dict]:
        """
        Get a summary of a conversation

        Args:
            conversation_id: The ID of the conversation to summarize

        Returns:
            Dictionary with conversation summary information, or None if not found
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return None

        return {
            "conversation_id": conversation.conversation_id,
            "turn_count": len(conversation.turns),
            "created_at": conversation.created_at.isoformat(),
            "last_activity": conversation.last_activity.isoformat(),
            "is_active": conversation.is_active,
            "metadata_keys": list(conversation.metadata.keys()) if conversation.metadata else []
        }

    async def clear_all_conversations(self) -> int:
        """
        Clear all conversations from memory

        Returns:
            Number of conversations cleared
        """
        count = len(self._conversations)
        self._conversations.clear()
        return count