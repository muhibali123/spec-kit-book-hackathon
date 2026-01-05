"""
Demo script to demonstrate the Gemini LLM adapter functionality.
This script shows how to use the new adapter with the RAG agent.
"""
import asyncio
import os
from src.adapters.llm.adapter_factory import create_llm_adapter
from src.agents.rag_agent import RAGAgent
from src.agents.agent_config import AgentConfig
from src.models.data_models import RetrievedContext, ContextChunk


async def demo_gemini_adapter():
    """
    Demonstrate the Gemini adapter functionality.
    """
    print("=== Gemini LLM Adapter Demo ===\n")

    # Set up environment variables for the demo
    # In a real application, these would be set in your .env file
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  GEMINI_API_KEY not set. This demo will show the structure but won't make real API calls.")
        print("To run with real API calls, set GEMINI_API_KEY environment variable.\n")
        return

    try:
        # Create a Gemini adapter directly
        print("1. Creating Gemini adapter...")
        gemini_adapter = create_llm_adapter("gemini")
        print(f"✓ Created Gemini adapter with model: {gemini_adapter.model_name}\n")

        # Create agent config for Gemini
        print("2. Creating RAG agent with Gemini configuration...")
        agent_config = AgentConfig(
            llm_provider="gemini",
            model_name="gemini-pro",
            temperature=0.7,
            max_tokens=500
        )

        # Create RAG agent with the Gemini adapter
        rag_agent = RAGAgent(config=agent_config)
        print("✓ Created RAG agent configured for Gemini\n")

        # Create sample context for testing
        print("3. Creating sample context...")
        sample_context = RetrievedContext(
            context_chunks=[
                ContextChunk(
                    chunk_id="doc1-chunk1",
                    content="Large Language Models (LLMs) are advanced AI systems trained on vast amounts of text data. They can understand and generate human-like text based on the patterns they learned during training.",
                    source_document="llm_basics.pdf",
                    source_section="Introduction",
                    relevance_score=0.95
                ),
                ContextChunk(
                    chunk_id="doc1-chunk2",
                    content="Gemini is Google's family of large language models. It's designed to handle various types of inputs including text, images, audio, and code.",
                    source_document="gemini_overview.pdf",
                    source_section="Model Overview",
                    relevance_score=0.92
                )
            ],
            relevance_scores=[0.95, 0.92]
        )
        print("✓ Created sample context with 2 chunks\n")

        # Test the agent's generate_answer method
        print("4. Testing generate_answer with Gemini...")
        query = "What is Gemini and how does it differ from other LLMs?"

        # This would make a real API call to Gemini if the key is valid
        try:
            answer = await rag_agent.generate_answer(
                query=query,
                retrieved_context=sample_context
            )
            print(f"✓ Generated answer: {answer[:100]}...\n")
        except Exception as e:
            print(f"⚠️  Could not generate answer (likely due to API key limitations): {e}\n")

        # Test the agent's validate_answer method
        print("5. Testing validate_answer with Gemini...")
        test_answer = "Gemini is Google's family of large language models that can handle various input types."

        try:
            is_valid = await rag_agent.validate_answer(
                query=query,
                answer=test_answer,
                retrieved_context=sample_context
            )
            print(f"✓ Validation result: {'VALID' if is_valid else 'INVALID'}\n")
        except Exception as e:
            print(f"⚠️  Could not validate answer: {e}\n")

        # Test the agent's extract_citations method
        print("6. Testing extract_citations with Gemini...")
        test_answer_with_citations = "According to the documentation, Gemini can handle various input types including text, images, and audio (from gemini_overview.pdf)."

        try:
            citations = await rag_agent.extract_citations(
                answer=test_answer_with_citations,
                retrieved_context=sample_context
            )
            print(f"✓ Extracted {len(citations)} citations\n")
        except Exception as e:
            print(f"⚠️  Could not extract citations: {e}\n")

        print("✅ Demo completed successfully!")
        print("\nKey points:")
        print("- The RAG agent now uses the LLM adapter abstraction")
        print("- You can switch between OpenAI and Gemini by changing the llm_provider config")
        print("- The same RAG agent interface works with different LLM providers")
        print("- Configuration can be managed through environment variables")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_gemini_adapter())