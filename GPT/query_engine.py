"""
Phase 3: Query Retrieval & Context Building

This module implements the QueryEngine class for retrieving relevant context
from the vector database based on user queries.
"""

import re
from typing import List, Dict, Optional, Tuple
from vector_store import ChromaVectorStore


class QueryEngine:
    """
    Handles query preprocessing, vector search, result filtering, and context building.

    This class provides the retrieval component of the RAG system, taking user
    questions and returning relevant context chunks from the vector database.
    """

    def __init__(self, vector_store: ChromaVectorStore):
        """
        Initialize the QueryEngine with a vector store.

        Args:
            vector_store: Initialized ChromaVectorStore instance
        """
        self.vector_store = vector_store

    def preprocess_query(self, query: str) -> str:
        """
        Preprocess and normalize user query text.

        - Strip whitespace
        - Convert to lowercase
        - Remove extra punctuation
        - Handle common variations

        Args:
            query: Raw user query string

        Returns:
            Normalized query string
        """
        if not query:
            return ""

        # Strip whitespace
        query = query.strip()

        # Convert to lowercase
        query = query.lower()

        # Remove extra punctuation but keep question marks
        query = re.sub(r'[^\w\s\?]', ' ', query)

        # Remove extra whitespace
        query = ' '.join(query.split())

        return query

    def search_similar(self, query: str, k: int = 5) -> List[Dict]:
        """
        Search for similar chunks in the vector database.

        Args:
            query: User query string
            k: Number of results to return

        Returns:
            List of result dictionaries with content, metadata, and scores
        """
        return self.vector_store.search(query, k=k)

    def filter_results(self, results: List[Dict], score_threshold: float = 0.5) -> List[Dict]:
        """
        Filter results by relevance score.

        Args:
            results: Search results from vector_store.search()
            score_threshold: Minimum similarity score to keep

        Returns:
            Filtered list of results
        """
        return [r for r in results if r.get('similarity_score', 0) >= score_threshold]

    def deduplicate_results(self, results: List[Dict], similarity_threshold: float = 0.95) -> List[Dict]:
        """
        Remove duplicate or very similar results to avoid redundancy.

        Args:
            results: Filtered search results
            similarity_threshold: Threshold for considering chunks similar

        Returns:
            Deduplicated list of results
        """
        if not results:
            return results

        # Simple deduplication based on content similarity
        # For now, just remove exact duplicates
        seen_content = set()
        deduplicated = []

        for result in results:
            content = result.get('content', '').strip()
            if content not in seen_content:
                seen_content.add(content)
                deduplicated.append(result)

        return deduplicated

    def build_context(self, results: List[Dict], max_length: int = 2000) -> str:
        """
        Build formatted context string from search results.

        Args:
            results: List of search result dictionaries
            max_length: Maximum context length in characters

        Returns:
            Formatted context string for LLM consumption
        """
        if not results:
            return "No relevant information found."

        context_parts = []
        total_length = 0

        for i, result in enumerate(results, 1):
            source = result.get('metadata', {}).get('source', 'Unknown')
            content = result.get('content', '').strip()
            score = result.get('similarity_score', 0)

            # Format this result
            part = f"[{i}. From {source}] (Relevance: {score:.2f})\n{content}\n"

            # Check if adding this would exceed max_length
            if total_length + len(part) > max_length and context_parts:
                break

            context_parts.append(part)
            total_length += len(part)

        # Join all parts
        context = "RETRIEVED CONTEXT:\n\n" + "\n".join(context_parts)

        # Add summary note
        scores = [r.get('similarity_score', 0) for r in results[:len(context_parts)]]
        if scores:
            avg_score = sum(scores) / len(scores)
            context += f"\nNote: Average relevance score: {avg_score:.2f}"

        return context

    def process_query(self, query: str, k: int = 5, score_threshold: float = 0.5) -> str:
        """
        Complete query processing pipeline.

        Args:
            query: Raw user query
            k: Number of initial search results
            score_threshold: Minimum relevance score

        Returns:
            Formatted context string ready for LLM
        """
        # Step 1: Preprocess query
        processed_query = self.preprocess_query(query)

        # Step 2: Search vector database
        results = self.search_similar(processed_query, k=k)

        # Step 3: Filter by score
        filtered_results = self.filter_results(results, score_threshold)

        # Step 4: Deduplicate
        deduplicated_results = self.deduplicate_results(filtered_results)

        # Step 5: Build context
        context = self.build_context(deduplicated_results)

        return context

    def get_stats(self) -> Dict:
        """
        Get statistics about the query engine and vector store.

        Returns:
            Dictionary with various statistics
        """
        return self.vector_store.get_stats()