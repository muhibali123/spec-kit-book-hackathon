from typing import List, Dict, Any, Optional
from src.models.data_models import RetrievedDocument


class FilteringService:
    """
    Service for filtering and ranking retrieved documents based on relevance scores and metadata
    """

    def __init__(self):
        pass

    async def filter_by_score_threshold(
        self,
        documents: List[RetrievedDocument],
        threshold: float
    ) -> List[RetrievedDocument]:
        """
        Filter documents based on similarity score threshold
        """
        return [doc for doc in documents if doc.score >= threshold]

    async def filter_by_metadata(
        self,
        documents: List[RetrievedDocument],
        filters: Optional[Dict[str, Any]]
    ) -> List[RetrievedDocument]:
        """
        Filter documents based on metadata criteria
        """
        if not filters:
            return documents

        filtered_docs = []
        for doc in documents:
            include = True
            for key, value in filters.items():
                if key in doc.payload and doc.payload[key] != value:
                    include = False
                    break
            if include:
                filtered_docs.append(doc)

        return filtered_docs

    async def rank_documents(self, documents: List[RetrievedDocument]) -> List[RetrievedDocument]:
        """
        Rank documents by similarity score (highest first)
        """
        return sorted(documents, key=lambda x: x.score, reverse=True)