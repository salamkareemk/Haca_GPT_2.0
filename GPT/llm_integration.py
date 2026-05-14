"""
Phase 4: LLM Integration & Answer Generation

This module implements the LLM integration for generating intelligent answers
based on retrieved context from the vector database.
"""

import os
import re
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate response from prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available and configured."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider for answer generation."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: Model to use (gpt-3.5-turbo, gpt-4, etc.)
        """
        try:
            import openai
            self.openai = openai
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        self.openai.api_key = self.api_key
        self.model = model

    def generate(self, prompt: str) -> str:
        """
        Generate response using OpenAI API.

        Args:
            prompt: Complete prompt with context and question

        Returns:
            Generated response string
        """
        try:
            response = self.openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return bool(self.api_key)


class MockProvider(LLMProvider):
    """Mock provider for testing without API calls."""

    def __init__(self):
        self.responses = [
            "Based on the information available, I can help you with details about HACA courses and programs.",
            "I'd be happy to provide information about fees, batches, and admission requirements.",
            "For the most current information, please contact our admissions office directly."
        ]

    def generate(self, prompt: str) -> str:
        """Return a mock response."""
        # Simple mock - return first response or extract from prompt
        if "fees" in prompt.lower():
            return "Course fees vary by program. Please check our current fee structure for detailed information."
        elif "batches" in prompt.lower():
            return "We offer multiple batches throughout the year. Contact admissions for the latest schedule."
        else:
            return self.responses[0]

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True


class PromptBuilder:
    """Builds structured prompts for LLM consumption."""

    def __init__(self, institution_name: str = "HACA"):
        """
        Initialize prompt builder.

        Args:
            institution_name: Name of the institution
        """
        self.institution = institution_name

    def build_prompt(self, user_query: str, context: str) -> str:
        """
        Build a complete prompt with system instructions, context, and user query.

        Args:
            user_query: The user's question
            context: Retrieved context from vector database

        Returns:
            Complete prompt string
        """
        system_prompt = f"""You are a helpful assistant for {self.institution} educational institution.

Your role is to:
1. Answer questions about courses, batches, fees, faculty, policies, and admissions
2. Provide accurate information from the provided context only
3. Be professional, concise, and encouraging
4. Admit when information is not available in the context
5. Suggest next steps when appropriate (e.g., "contact admissions for current availability")

Important Guidelines:
- ONLY use information from the provided RETRIEVED CONTEXT
- If the answer is not in the context, say: "I don't have that specific information. Please contact our admissions office."
- Format fees with currency symbol (₹)
- For dates, use DD-MM-YYYY format when possible
- Be helpful and encouraging about learning opportunities
- Keep responses clear and well-structured
- If multiple relevant pieces of information exist, summarize them logically

Context Usage:
- Reference specific sources when providing information
- Combine related information from different sources
- Prioritize the most relevant and recent information"""

        user_prompt = f"""

RETRIEVED CONTEXT:
{context}

USER QUESTION: {user_query}

Please provide a helpful and accurate answer based on the context above."""

        return system_prompt + user_prompt


class ResponseProcessor:
    """Processes and cleans LLM responses."""

    def __init__(self):
        """Initialize response processor."""
        self.replacements = {
            "HACA": "HACA",  # Ensure consistent capitalization
        }

    def clean_response(self, text: str) -> str:
        """
        Clean and format the LLM response.

        Args:
            text: Raw response from LLM

        Returns:
            Cleaned response string
        """
        if not text:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Fix common formatting issues
        text = text.replace("  ", " ")
        text = text.replace(" ,", ",")
        text = text.replace(" .", ".")

        # Ensure proper sentence endings
        if not text.endswith(('.', '!', '?')):
            text += "."

        return text

    def add_citations(self, response: str, sources: List[str]) -> str:
        """
        Add source citations to the response.

        Args:
            response: Cleaned response
            sources: List of source file names

        Returns:
            Response with citations
        """
        if not sources:
            return response

        # Remove duplicates and sort
        unique_sources = sorted(list(set(sources)))

        citation_text = f"\n\nSources: {', '.join(unique_sources)}"
        return response + citation_text

    def validate_response(self, response: str) -> bool:
        """
        Validate response quality.

        Args:
            response: Response to validate

        Returns:
            True if response passes validation
        """
        # Minimum length check
        if len(response) < 20:
            return False

        # Check for repeated text (potential hallucination)
        words = response.split()
        if len(words) > 10:
            first_10 = ' '.join(words[:10])
            if response.count(first_10) > 1:
                return False

        # Check for error messages
        error_indicators = ["error generating", "api error", "connection failed"]
        if any(indicator in response.lower() for indicator in error_indicators):
            return False

        return True


class HACARagPipeline:
    """
    Complete Retrieval-Augmented Generation pipeline for HACA GPT.

    Combines query retrieval, prompt building, LLM generation, and response processing.
    """

    def __init__(self,
                 vector_store,
                 llm_provider: LLMProvider,
                 query_engine):
        """
        Initialize the RAG pipeline.

        Args:
            vector_store: Initialized ChromaVectorStore
            llm_provider: LLM provider instance
            query_engine: Initialized QueryEngine
        """
        self.vector_store = vector_store
        self.llm = llm_provider
        self.query_engine = query_engine
        self.prompt_builder = PromptBuilder()
        self.response_processor = ResponseProcessor()

    def answer_question(self, user_query: str, k: int = 5, score_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Complete pipeline: query → retrieve → generate → process → return

        Args:
            user_query: User's question
            k: Number of context chunks to retrieve
            score_threshold: Minimum relevance score for context

        Returns:
            Dictionary with answer, sources, confidence, and metadata
        """
        try:
            # Step 1: Retrieve context
            context = self.query_engine.process_query(user_query, k=k, score_threshold=score_threshold)

            # Step 2: Build prompt
            prompt = self.prompt_builder.build_prompt(user_query, context)

            # Step 3: Generate answer
            raw_answer = self.llm.generate(prompt)

            # Step 4: Post-process response
            clean_answer = self.response_processor.clean_response(raw_answer)

            # Step 5: Add citations
            sources = self._extract_sources(context)
            final_answer = self.response_processor.add_citations(clean_answer, sources)

            # Step 6: Calculate confidence
            confidence = self._calculate_confidence(raw_answer, context)

            # Step 7: Validate response
            is_valid = self.response_processor.validate_response(final_answer)

            return {
                "answer": final_answer,
                "sources": sources,
                "confidence": confidence,
                "query": user_query,
                "context_length": len(context),
                "is_valid": is_valid,
                "raw_answer": raw_answer if not is_valid else None  # Include raw for debugging if invalid
            }

        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "query": user_query,
                "context_length": 0,
                "is_valid": False,
                "error": str(e)
            }

    def _extract_sources(self, context: str) -> List[str]:
        """
        Extract source file names from context string.

        Args:
            context: Formatted context string

        Returns:
            List of source file names
        """
        import re
        # Match patterns like "[1. From filename.txt]"
        sources = re.findall(r'\[.*?\s+From\s+([^\]]+)\]', context)
        return list(set(sources))

    def _calculate_confidence(self, response: str, context: str) -> float:
        """
        Estimate confidence in the response.

        Args:
            response: Generated response
            context: Retrieved context

        Returns:
            Confidence score between 0.0 and 1.0
        """
        confidence = 0.7  # Base confidence

        response_lower = response.lower()

        # Reduce confidence for uncertainty indicators
        uncertainty_keywords = [
            "i don't know", "not sure", "unclear", "insufficient",
            "cannot find", "no information", "unable to determine"
        ]

        if any(keyword in response_lower for keyword in uncertainty_keywords):
            confidence -= 0.2

        # Increase confidence for longer, more detailed responses
        if len(response) > 200:
            confidence += 0.1

        # Increase confidence if context was substantial
        if len(context) > 500:
            confidence += 0.1

        # Ensure bounds
        return max(0.0, min(1.0, confidence))

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the pipeline components.

        Returns:
            Dictionary with various statistics
        """
        return {
            "llm_available": self.llm.is_available(),
            "vector_store_stats": self.query_engine.get_stats(),
            "pipeline_components": ["QueryEngine", "PromptBuilder", "LLMProvider", "ResponseProcessor"]
        }