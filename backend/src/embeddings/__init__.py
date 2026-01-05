"""
Main entry point for the embeddings generation module.
"""
from .generator import EmbeddingGenerator
from .validator import Validator
from .cohere_client import CohereClient
from .batch_processor import BatchProcessor

__all__ = ['EmbeddingGenerator', 'Validator', 'CohereClient', 'BatchProcessor']