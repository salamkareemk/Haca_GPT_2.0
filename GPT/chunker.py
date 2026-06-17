from typing import List, Dict, Any
import tiktoken
import os
from pathlib import Path

class TextChunker:
    def __init__(self, chunk_tokens: int = 400, overlap_tokens: int = 80):
        self.chunk_tokens = chunk_tokens
        self.overlap_tokens = overlap_tokens
        self.enc = tiktoken.get_encoding("cl100k_base")
    
    def chunk_text(self, text: str) -> List[str]:
        """Chunk text by tokens with overlap."""
        tokens = self.enc.encode(text)
        chunks = []
        start = 0

        while start < len(tokens):
            end = start + self.chunk_tokens
            chunk = self.enc.decode(tokens[start:end])
            chunks.append(chunk)
            start = end - self.overlap_tokens
            if start < 0:
                start = 0

        return chunks

    def chunk_text_with_metadata(self, text: str, source: str, file_type: str) -> List[Dict[str, Any]]:
        """Chunk text and attach metadata (source, line numbers, chunk index)."""
        lines = text.split('\n')
        chunks = self.chunk_text(text)
        
        chunks_with_metadata = []
        current_line = 0
        
        for chunk_idx, chunk in enumerate(chunks):
            # Count lines in chunk
            chunk_lines = chunk.split('\n')
            start_line = current_line
            end_line = current_line + len(chunk_lines)
            current_line = end_line - self.overlap_tokens // 10  # Approximate overlap
            
            chunks_with_metadata.append({
                "content": chunk,
                "source": source,
                "file_type": file_type,
                "start_line": start_line,
                "end_line": end_line,
                "chunk_index": chunk_idx,
            })
        
        return chunks_with_metadata

    def read_file(self, file_path: str) -> str:
        """Read file content with robust encoding handling."""
        # Try UTF-8 first, then fall back to latin-1 (handles most Windows files)
        for enc in ('utf-8-sig', 'utf-8', 'latin-1'):
            try:
                with open(file_path, 'r', encoding=enc, errors='ignore') as f:
                    return f.read()
            except (UnicodeDecodeError, LookupError):
                continue
        # Last resort — binary read decoded loosely
        with open(file_path, 'rb') as f:
            return f.read().decode('utf-8', errors='replace')

    def process_data_files(self, data_dir: str = "backend/data") -> List[Dict[str, Any]]:
        """Process all data files in the data directory."""
        all_chunks = []
        
        if not os.path.exists(data_dir):
            print(f"Directory {data_dir} not found")
            return all_chunks
        
        # Supported file types
        supported_files = {
            '.txt': 'txt',
            '.md': 'markdown',
            '.csv': 'csv'
        }
        
        for file_name in os.listdir(data_dir):
            file_path = os.path.join(data_dir, file_name)
            _, ext = os.path.splitext(file_name)
            
            if ext in supported_files:
                try:
                    print(f"Processing {file_name}...")
                    content = self.read_file(file_path)
                    file_type = supported_files[ext]
                    
                    chunks = self.chunk_text_with_metadata(
                        content, 
                        source=file_name,
                        file_type=file_type
                    )
                    all_chunks.extend(chunks)
                    print(f"  [OK] Created {len(chunks)} chunks from {file_name}")
                except Exception as e:
                    print(f"  [ERROR] Error processing {file_name}: {e}")
        
        return all_chunks


# Legacy function for backward compatibility
def chunk_text(text: str, chunk_tokens: int = 400, overlap_tokens: int = 80) -> List[str]:
    chunker = TextChunker(chunk_tokens, overlap_tokens)
    return chunker.chunk_text(text)
