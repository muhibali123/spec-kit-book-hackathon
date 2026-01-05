import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.services.conversation_service import ConversationService
from src.models.data_models import ConversationContext, ConversationTurn
from src.config.settings import settings


class TestConversationService:
    """Test the ConversationService class"""

    async def test_create_conversation_without_initial_turn(self):
        """Test creating a conversation without initial turn"""
        service = ConversationService()
        conversation = await service.create_conversation()

        assert conversation is not None
        assert conversation.conversation_id is not None
        assert len(conversation.turns) == 0
        assert conversation.is_active is True
        assert conversation.created_at <= datetime.now()
        assert conversation.last_activity <= datetime.now()

    async def test_create_conversation_with_initial_turn(self):
        """Test creating a conversation with initial turn"""
        service = ConversationService()
        conversation = await service.create_conversation(
            initial_query="Hello",
            initial_response="Hi there!"
        )

        assert conversation is not None
        assert len(conversation.turns) == 1
        assert conversation.turns[0].user_query == "Hello"
        assert conversation.turns[0].system_response == "Hi there!"

    async def test_create_conversation_with_custom_id(self):
        """Test creating a conversation with a custom ID"""
        service = ConversationService()
        custom_id = "test-conversation-id"
        conversation = await service.create_conversation(conversation_id=custom_id)

        assert conversation.conversation_id == custom_id

    async def test_get_conversation_exists(self):
        """Test retrieving an existing conversation"""
        service = ConversationService()
        conversation = await service.create_conversation()

        retrieved = await service.get_conversation(conversation.conversation_id)

        assert retrieved is not None
        assert retrieved.conversation_id == conversation.conversation_id

    async def test_get_conversation_not_exists(self):
        """Test retrieving a non-existing conversation"""
        service = ConversationService()

        retrieved = await service.get_conversation("non-existent-id")

        assert retrieved is None

    async def test_add_turn_to_conversation(self):
        """Test adding a turn to an existing conversation"""
        service = ConversationService()
        conversation = await service.create_conversation()

        updated_conversation = await service.add_turn(
            conversation_id=conversation.conversation_id,
            user_query="How are you?",
            system_response="I'm doing well, thank you!"
        )

        assert updated_conversation is not None
        assert len(updated_conversation.turns) == 1
        assert updated_conversation.turns[0].user_query == "How are you?"
        assert updated_conversation.turns[0].system_response == "I'm doing well, thank you!"

    async def test_add_turn_to_nonexistent_conversation(self):
        """Test adding a turn to a non-existent conversation"""
        service = ConversationService()

        result = await service.add_turn(
            conversation_id="non-existent-id",
            user_query="Test query",
            system_response="Test response"
        )

        assert result is None

    async def test_add_turn_with_context_summary(self):
        """Test adding a turn with context summary"""
        service = ConversationService()
        conversation = await service.create_conversation()

        updated_conversation = await service.add_turn(
            conversation_id=conversation.conversation_id,
            user_query="What's the weather?",
            system_response="It's sunny today",
            context_summary="User asking about weather conditions"
        )

        assert updated_conversation is not None
        assert len(updated_conversation.turns) == 1
        assert updated_conversation.turns[0].context_summary == "User asking about weather conditions"

    async def test_update_conversation_metadata(self):
        """Test updating conversation metadata"""
        service = ConversationService()
        conversation = await service.create_conversation()

        success = await service.update_conversation_metadata(
            conversation_id=conversation.conversation_id,
            metadata={"user_id": "user123", "topic": "greeting"}
        )

        assert success is True

        # Retrieve the conversation to verify metadata was updated
        updated_conversation = await service.get_conversation(conversation.conversation_id)
        assert updated_conversation.metadata["user_id"] == "user123"
        assert updated_conversation.metadata["topic"] == "greeting"

    async def test_update_conversation_metadata_nonexistent(self):
        """Test updating metadata for a non-existent conversation"""
        service = ConversationService()

        success = await service.update_conversation_metadata(
            conversation_id="non-existent-id",
            metadata={"test": "value"}
        )

        assert success is False

    async def test_delete_conversation(self):
        """Test deleting a conversation"""
        service = ConversationService()
        conversation = await service.create_conversation()

        success = await service.delete_conversation(conversation.conversation_id)

        assert success is True

        # Verify the conversation no longer exists
        retrieved = await service.get_conversation(conversation.conversation_id)
        assert retrieved is None

    async def test_delete_nonexistent_conversation(self):
        """Test deleting a non-existent conversation"""
        service = ConversationService()

        success = await service.delete_conversation("non-existent-id")

        assert success is False

    async def test_list_active_conversations(self):
        """Test listing active conversations"""
        service = ConversationService()

        # Create a few conversations
        conv1 = await service.create_conversation(initial_query="Q1", initial_response="A1")
        conv2 = await service.create_conversation(initial_query="Q2", initial_response="A2")

        conversations = await service.list_active_conversations()

        assert len(conversations) == 2
        conversation_ids = [c.conversation_id for c in conversations]
        assert conv1.conversation_id in conversation_ids
        assert conv2.conversation_id in conversation_ids

    async def test_conversation_expiration(self):
        """Test that expired conversations are handled properly"""
        service = ConversationService()

        # Create a conversation and manually set its last activity to be in the past
        conversation = await service.create_conversation()
        past_time = datetime.now() - timedelta(hours=settings.conversation_expiry_hours + 1)
        service._conversations[conversation.conversation_id].last_activity = past_time

        # Try to retrieve the conversation - it should be expired and return None
        retrieved = await service.get_conversation(conversation.conversation_id)
        assert retrieved is None

        # Verify it's no longer in the store
        assert conversation.conversation_id not in service._conversations

    async def test_cleanup_expired_conversations(self):
        """Test cleaning up expired conversations"""
        service = ConversationService()

        # Create conversations with expired timestamps
        conv1 = await service.create_conversation()
        conv2 = await service.create_conversation()

        # Set their last activity times to be in the past beyond expiry
        past_time = datetime.now() - timedelta(hours=settings.conversation_expiry_hours + 1)
        service._conversations[conv1.conversation_id].last_activity = past_time
        service._conversations[conv2.conversation_id].last_activity = past_time

        # Clean up expired conversations
        removed_count = await service.cleanup_expired_conversations()

        assert removed_count == 2
        assert len(service._conversations) == 0

    async def test_get_conversation_summary(self):
        """Test getting a conversation summary"""
        service = ConversationService()
        conversation = await service.create_conversation(
            initial_query="Hello",
            initial_response="Hi there!"
        )

        summary = await service.get_conversation_summary(conversation.conversation_id)

        assert summary is not None
        assert summary["conversation_id"] == conversation.conversation_id
        assert summary["turn_count"] == 1
        assert summary["is_active"] is True

    async def test_get_conversation_summary_nonexistent(self):
        """Test getting summary for a non-existent conversation"""
        service = ConversationService()

        summary = await service.get_conversation_summary("non-existent-id")

        assert summary is None

    async def test_clear_all_conversations(self):
        """Test clearing all conversations"""
        service = ConversationService()

        # Create a few conversations
        await service.create_conversation()
        await service.create_conversation()
        await service.create_conversation()

        assert len(service._conversations) == 3

        # Clear all conversations
        cleared_count = await service.clear_all_conversations()

        assert cleared_count == 3
        assert len(service._conversations) == 0

    async def test_generate_context_summary(self):
        """Test generating a context summary for a conversation"""
        service = ConversationService()
        conversation = await service.create_conversation(
            initial_query="What is AI?",
            initial_response="AI is artificial intelligence"
        )

        # Add more turns to have content for summarization
        await service.add_turn(
            conversation_id=conversation.conversation_id,
            user_query="How does it work?",
            system_response="AI works by processing data and finding patterns"
        )
        await service.add_turn(
            conversation_id=conversation.conversation_id,
            user_query="Give examples",
            system_response="Examples include machine learning and NLP"
        )

        summary = await service.generate_context_summary(conversation.conversation_id)

        assert summary is not None
        assert "AI" in summary
        assert "Q:" in summary
        assert "A:" in summary

    async def test_generate_context_summary_nonexistent(self):
        """Test generating context summary for non-existent conversation"""
        service = ConversationService()

        summary = await service.generate_context_summary("non-existent-id")

        assert summary is None

    async def test_get_recent_context(self):
        """Test getting recent context from a conversation"""
        service = ConversationService()
        conversation = await service.create_conversation(
            initial_query="First query",
            initial_response="First response"
        )

        # Add more turns
        await service.add_turn(
            conversation_id=conversation.conversation_id,
            user_query="Second query",
            system_response="Second response"
        )
        await service.add_turn(
            conversation_id=conversation.conversation_id,
            user_query="Third query",
            system_response="Third response"
        )

        # Get recent context (last 2 turns)
        recent_context = await service.get_recent_context(conversation.conversation_id, num_turns=2)

        assert recent_context is not None
        assert len(recent_context) == 2
        assert recent_context[0]["user_query"] == "Second query"
        assert recent_context[1]["system_response"] == "Third response"

    async def test_get_recent_context_nonexistent(self):
        """Test getting recent context for non-existent conversation"""
        service = ConversationService()

        recent_context = await service.get_recent_context("non-existent-id")

        assert recent_context is None

    async def test_conversation_turn_limit(self):
        """Test that conversation turns are limited according to settings"""
        # Temporarily modify the setting for this test
        original_max_turns = settings.max_conversation_turns
        settings.max_conversation_turns = 3

        try:
            service = ConversationService()
            conversation = await service.create_conversation(
                initial_query="Query 1",
                initial_response="Response 1"
            )

            # Add more turns than the limit
            await service.add_turn(
                conversation_id=conversation.conversation_id,
                user_query="Query 2",
                system_response="Response 2"
            )
            await service.add_turn(
                conversation_id=conversation.conversation_id,
                user_query="Query 3",
                system_response="Response 3"
            )
            await service.add_turn(
                conversation_id=conversation.conversation_id,
                user_query="Query 4",
                system_response="Response 4"
            )
            await service.add_turn(
                conversation_id=conversation.conversation_id,
                user_query="Query 5",
                system_response="Response 5"
            )

            # Get the conversation and verify only the last 3 turns remain
            updated_conversation = await service.get_conversation(conversation.conversation_id)
            assert len(updated_conversation.turns) == 3

            # Verify the oldest turns were removed (keeping the 3 most recent)
            assert updated_conversation.turns[0].user_query == "Query 3"
            assert updated_conversation.turns[1].user_query == "Query 4"
            assert updated_conversation.turns[2].user_query == "Query 5"

        finally:
            # Restore original setting
            settings.max_conversation_turns = original_max_turns

    async def test_conversation_lifecycle(self):
        """Test the full lifecycle of a conversation"""
        service = ConversationService()

        # Create conversation
        conversation = await service.create_conversation(
            initial_query="Hello",
            initial_response="Hi there!"
        )
        assert conversation is not None
        assert len(conversation.turns) == 1

        # Add several turns
        for i in range(2, 5):
            result = await service.add_turn(
                conversation_id=conversation.conversation_id,
                user_query=f"Query {i}",
                system_response=f"Response {i}"
            )
            assert result is not None

        # Verify conversation has multiple turns
        updated_conversation = await service.get_conversation(conversation.conversation_id)
        assert len(updated_conversation.turns) == 4

        # Update metadata
        success = await service.update_conversation_metadata(
            conversation_id=conversation.conversation_id,
            metadata={"topic": "test_conversation", "complexity": "medium"}
        )
        assert success is True

        # Verify metadata was added
        updated_conversation = await service.get_conversation(conversation.conversation_id)
        assert updated_conversation.metadata["topic"] == "test_conversation"
        assert updated_conversation.metadata["complexity"] == "medium"

        # Get summary
        summary = await service.get_conversation_summary(conversation.conversation_id)
        assert summary["turn_count"] == 4
        assert summary["is_active"] is True

        # Delete conversation
        success = await service.delete_conversation(conversation.conversation_id)
        assert success is True

        # Verify conversation no longer exists
        retrieved = await service.get_conversation(conversation.conversation_id)
        assert retrieved is None