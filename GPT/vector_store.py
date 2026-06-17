"""
Vector Store Module - ChromaDB Integration

This module handles:
1. Creating embeddings from text chunks (sentence-transformers)
2. Storing embeddings in ChromaDB
3. Semantic search and retrieval
"""

from typing import List, Dict, Any, Optional
import chromadb
from sentence_transformers import SentenceTransformer
import os
from pathlib import Path


class EmbeddingGenerator:
    """Generate embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model.
        
        Args:
            model_name: Sentence-transformers model. Default: all-MiniLM-L6-v2 (384-dim)
        """
        print(f"Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        print(f"[OK] Model loaded. Embedding dimension: {self.model.get_embedding_dimension()}")
    
    def embed_text(self, text: str) -> List[float]:
        """
        Embed single text into vector.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats (embedding vector)
        """
        return self.model.encode(text).tolist()
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts into vectors.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        return [self.model.encode(text).tolist() for text in texts]


class ChromaVectorStore:
    """
    ChromaDB vector store for HACA data.
    
    Handles:
    - Collection creation
    - Document storage with embeddings
    - Semantic search
    - Metadata management
    """
    
    def __init__(self, 
                 db_path: str = "./chroma3.db",
                 collection_name: str = "haca_documents",
                 embedding_model: str = "all-MiniLM-L6-v2"):
        """
        Initialize ChromaDB vector store.
        
        Args:
            db_path: Path to ChromaDB persistent storage
            collection_name: Name of the collection
            embedding_model: Sentence-transformers model name
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Create embeddings generator
        self.embedding_generator = EmbeddingGenerator(embedding_model)
        
        # Initialize ChromaDB client
        print(f"\nInitializing ChromaDB at {db_path}...")
        self.client = chromadb.PersistentClient(path=db_path)
        
        # Get existing collection or create a new one — never errors on duplicates
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        doc_count = self.collection.count()
        if doc_count > 0:
            print(f"[OK] Connected to existing collection: {collection_name}")
            print(f"  Current documents: {doc_count}")
        else:
            print(f"[OK] New collection created: {collection_name}")
    
    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add document chunks to vector store.
        
        Args:
            chunks: List of chunk dictionaries with metadata
                   Expected format:
                   {
                       "content": str,
                       "source": str,
                       "file_type": str,
                       "start_line": int,
                       "end_line": int,
                       "chunk_index": int
                   }
        
        Returns:
            Number of chunks added
        """
        if not chunks:
            print("No chunks to add")
            return 0
        
        print(f"\nAdding {len(chunks)} chunks to ChromaDB...")
        
        # Extract data from chunks
        documents = [chunk["content"] for chunk in chunks]
        ids = [f"chunk_{i}" for i in range(len(chunks))]
        metadatas = [
            {
                "source": chunk["source"],
                "file_type": chunk["file_type"],
                "start_line": chunk.get("start_line", 0),
                "end_line": chunk.get("end_line", 0),
                "chunk_index": chunk.get("chunk_index", 0)
            }
            for chunk in chunks
        ]
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.embedding_generator.embed_texts(documents)
        
        # Add to collection
        self.collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=ids,
            metadatas=metadatas
        )
        
        # PersistentClient auto-persists on every write — no manual call needed
        print(f"[OK] Added {len(chunks)} chunks to vector store")
        print(f"[OK] Total documents in collection: {self.collection.count()}")
        
        return len(chunks)
    
    def search(self, 
               query: str, 
               k: int = 5,
               score_threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant chunks using semantic similarity.
        
        Args:
            query: Search query text
            k: Number of results to return. Default: 5
            score_threshold: Minimum similarity score (0-1). Default: None (no threshold)
        
        Returns:
            List of matching chunks with similarity scores
            Format:
            [
                {
                    "id": "chunk_0",
                    "content": "text...",
                    "similarity_score": 0.87,
                    "source": "batches.txt",
                    "file_type": "txt",
                    "start_line": 0,
                    "end_line": 13,
                    "chunk_index": 0
                },
                ...
            ]
        """
        if self.collection.count() == 0:
            print("Vector store is empty. No results found.")
            return []
        
        print(f"Searching for: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedding_generator.embed_text(query)
        
        # Search in collection
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i]
                # Convert distance to similarity score (1 - normalized_distance)
                distance = results["distances"][0][i]
                similarity_score = 1 - (distance / 2)  # Normalize cosine distance to similarity
                
                formatted_results.append({
                    "id": results["ids"][0][i] if "ids" in results else f"result_{i}",
                    "content": doc,
                    "similarity_score": round(similarity_score, 4),
                    "source": metadata.get("source", "unknown"),
                    "file_type": metadata.get("file_type", "unknown"),
                    "start_line": metadata.get("start_line", 0),
                    "end_line": metadata.get("end_line", 0),
                    "chunk_index": metadata.get("chunk_index", 0)
                })
        
        # Apply score threshold if provided
        if score_threshold:
            formatted_results = [r for r in formatted_results if r["similarity_score"] >= score_threshold]
        
        print(f"[OK] Found {len(formatted_results)} relevant chunks\n")
        
        return formatted_results
    
    def batch_search(self, 
                     queries: List[str], 
                     k: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search for multiple queries.
        
        Args:
            queries: List of search queries
            k: Number of results per query
        
        Returns:
            Dictionary mapping query to search results
        """
        results = {}
        for query in queries:
            results[query] = self.search(query, k=k)
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.collection.count(),
            "db_path": self.db_path,
            "embedding_dimension": self.embedding_generator.model.get_sentence_embedding_dimension()
        }
    
    def clear_collection(self) -> None:
        """Clear all documents from collection."""
        self.client.delete_collection(self.collection_name)
        self.collection = self.client.create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"[OK] Collection '{self.collection_name}' cleared")


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("ChromaDB Vector Store Example")
    print("=" * 60)
    
    # This is example code - uncomment to test
    # from chunker import TextChunker
    # 
    # # Step 1: Load chunks
    # print("\n1. Loading data chunks...")
    # chunker = TextChunker()
    # chunks = chunker.process_data_files('backend/data')
    # 
    # # Step 2: Create vector store
    # print("\n2. Creating vector store...")
    # vector_store = ChromaVectorStore()
    # 
    # # Step 3: Add chunks to vector store
    # print("\n3. Storing chunks...")
    # vector_store.add_chunks(chunks)
    # 
    # # Step 4: Search
    # print("\n4. Testing search...")
    # results = vector_store.search("What are the fees?", k=3)
    # for result in results:
    #     print(f"\n  Source: {result['source']}")
    #     print(f"  Score: {result['similarity_score']}")
    #     print(f"  Content: {result['content'][:100]}...")
