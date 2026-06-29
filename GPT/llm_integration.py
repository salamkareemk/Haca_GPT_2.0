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

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (if None, uses environment variable)
            model: Model to use (gpt-3.5-turbo, gpt-4, etc.)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY environment variable or pass api_key parameter.")

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")

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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1500,
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
        system_prompt = f"""You are HACA GPT - the official intelligent assistant for HACA (Haris & Co Academy), a leading professional skills training institute.

Your role:
1. Answer questions about HACA courses, batches, fees, faculty, policies, and admissions with accuracy and warmth
2. Provide information ONLY from the retrieved context - do not hallucinate or invent details
3. Be professional, encouraging, and approachable
4. Format your response in clean markdown when listing items
5. Format fees with the Rs. currency symbol
6. If information is not in the context, say: "I don't have that specific information. Please contact our admissions team at info@harisandcoacademy.com or WhatsApp +91 7736779775."

CRITICAL RULES - MUST FOLLOW:
- When asked to list people (faculty, mentors, staff), you MUST include EVERY SINGLE person found in the context. Do NOT stop after 3 or 4. Scan the entire context and list ALL of them.
- When listing faculty for a school/department, find everyone in that department and list them all completely.
- Do NOT add 'I don't have information' after a partial list if more people appear in the context.
- Do NOT truncate your answer. Always complete the full list before ending.
- If the context has 5 faculty members, your answer MUST show all 5.

Response Format Rules:
- Use bullet points or numbered lists for multiple items
- Bold key information like course names, fees, dates
- Keep responses complete - never cut off a list
- End EVERY response with a blank line, then exactly this section:

FOLLOW_UP_QUESTIONS:
1. [relevant follow-up question]
2. [relevant follow-up question]
3. [relevant follow-up question]

The follow-up questions must be short, relevant to what the user just asked, and genuinely helpful."""



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
        Preserves newlines and markdown structure.
        """
        if not text:
            return "I apologize, but I couldn't generate a response. Please try rephrasing your question."

        # Collapse multiple blank lines into a single blank line, but keep single newlines
        import re
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Fix inline spacing issues only (not across newlines)
        text = re.sub(r'[ \t]{2,}', ' ', text)
        text = text.replace(' ,', ',')
        text = text.replace(' .', '.')

        text = text.strip()

        # Ensure proper sentence endings
        if text and not text[-1] in ('.', '!', '?', '\n'):
            text += '.'

        return text


    def add_citations(self, response: str, sources: List[str]) -> str:
        """
        Add source citations to the response.
        """
        if not sources:
            return response

        # Clean source names — strip file extensions for display
        import os
        clean_sources = sorted(set(
            os.path.splitext(s)[0].replace('_', ' ').title() for s in sources
        ))

        citation_text = f"\n\n**Sources:** {', '.join(clean_sources)}"
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

    def answer_question(self, user_query: str, k: int = 8, score_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Complete pipeline: query → retrieve → generate → process → return
        """
        try:
            # Step 1: Retrieve context
            context = self.query_engine.process_query(user_query, k=k, score_threshold=score_threshold)

            # Step 2: Build prompt
            prompt = self.prompt_builder.build_prompt(user_query, context)

            # Step 3: Generate answer
            raw_answer = self.llm.generate(prompt)

            # Step 4: Parse follow-up questions out of the raw answer
            follow_ups = self._extract_follow_ups(raw_answer)
            answer_without_followups = self._strip_follow_ups(raw_answer)

            # Step 5: Post-process response (preserves markdown/newlines)
            clean_answer = self.response_processor.clean_response(answer_without_followups)

            # Step 6: Add citations
            sources = self._extract_sources(context)
            final_answer = self.response_processor.add_citations(clean_answer, sources)

            # Step 7: Calculate confidence
            confidence = self._calculate_confidence(raw_answer, context)

            # Step 8: Validate response
            is_valid = self.response_processor.validate_response(final_answer)

            return {
                "answer": final_answer,
                "sources": sources,
                "confidence": confidence,
                "query": user_query,
                "context_length": len(context),
                "is_valid": is_valid,
                "follow_ups": follow_ups,
                "raw_answer": raw_answer if not is_valid else None
            }

        except Exception as e:
            return {
                "answer": f"I apologize, but I encountered an error processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "query": user_query,
                "context_length": 0,
                "is_valid": False,
                "follow_ups": [],
                "error": str(e)
            }

    def _extract_follow_ups(self, raw_answer: str) -> List[str]:
        """Parse the FOLLOW_UP_QUESTIONS section from the raw LLM response."""
        import re
        follow_ups = []
        # Find the FOLLOW_UP_QUESTIONS block
        match = re.search(r'FOLLOW_UP_QUESTIONS:\s*\n(.*?)(?:\n\n|$)', raw_answer, re.DOTALL)
        if match:
            block = match.group(1)
            for line in block.strip().splitlines():
                # Strip leading "1. " or "- " numbering
                line = re.sub(r'^[\d]+\.\s*|^[-*]\s*', '', line).strip()
                if line:
                    follow_ups.append(line)
        return follow_ups[:3]  # Max 3

    def _strip_follow_ups(self, raw_answer: str) -> str:
        """Remove the FOLLOW_UP_QUESTIONS section from the answer text."""
        import re
        # Remove everything from FOLLOW_UP_QUESTIONS onward
        cleaned = re.sub(r'\n*FOLLOW_UP_QUESTIONS:.*', '', raw_answer, flags=re.DOTALL)
        return cleaned.strip()


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