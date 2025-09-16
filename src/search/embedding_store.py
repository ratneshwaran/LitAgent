from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

from ..models import Paper
from ..utils.logging import get_logger

logger = get_logger(__name__)


@dataclass
class EmbeddingRecord:
    """Record for storing paper embeddings with metadata"""
    paper_id: str
    title: str
    abstract: str
    embedding: np.ndarray
    doi: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    source: str = ""


class EmbeddingStore:
    """FAISS-based embedding storage for semantic search"""
    
    def __init__(self, store_path: Path = Path("data/embeddings")):
        self.store_path = store_path
        self.store_path.mkdir(parents=True, exist_ok=True)
        
        # FAISS index for fast similarity search
        self.index = None
        self.records: List[EmbeddingRecord] = []
        self.id_to_index: Dict[str, int] = {}
        
        # Load existing data if available
        self._load_store()
    
    def _load_store(self) -> None:
        """Load existing embedding store from disk"""
        index_file = self.store_path / "index.faiss"
        records_file = self.store_path / "records.pkl"
        metadata_file = self.store_path / "metadata.json"
        
        if index_file.exists() and records_file.exists():
            try:
                import faiss
                
                # Load FAISS index
                self.index = faiss.read_index(str(index_file))
                
                # Load records
                with open(records_file, 'rb') as f:
                    self.records = pickle.load(f)
                
                # Rebuild ID mapping
                self.id_to_index = {record.paper_id: i for i, record in enumerate(self.records)}
                
                # Load metadata
                if metadata_file.exists():
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                        logger.info(f"Loaded embedding store with {metadata.get('total_papers', 0)} papers")
                
            except Exception as e:
                logger.warning(f"Failed to load embedding store: {e}")
                self._initialize_empty_store()
        else:
            self._initialize_empty_store()
    
    def _initialize_empty_store(self) -> None:
        """Initialize empty FAISS index"""
        try:
            import faiss
            # Create empty index with 1536 dimensions (text-embedding-3-large)
            self.index = faiss.IndexFlatIP(1536)  # Inner product for cosine similarity
            self.records = []
            self.id_to_index = {}
        except ImportError:
            logger.error("FAISS not available. Install with: pip install faiss-cpu")
            raise
    
    def add_papers(self, papers: List[Paper], embeddings: List[np.ndarray]) -> None:
        """Add papers with their embeddings to the store"""
        if len(papers) != len(embeddings):
            raise ValueError("Papers and embeddings must have the same length")
        
        new_records = []
        for paper, embedding in zip(papers, embeddings):
            if paper.id in self.id_to_index:
                # Update existing record
                idx = self.id_to_index[paper.id]
                self.records[idx] = EmbeddingRecord(
                    paper_id=paper.id,
                    title=paper.title,
                    abstract=paper.abstract or "",
                    embedding=embedding,
                    doi=paper.doi,
                    year=paper.year,
                    venue=paper.venue,
                    source=paper.source
                )
            else:
                # Add new record
                record = EmbeddingRecord(
                    paper_id=paper.id,
                    title=paper.title,
                    abstract=paper.abstract or "",
                    embedding=embedding,
                    doi=paper.doi,
                    year=paper.year,
                    venue=paper.venue,
                    source=paper.source
                )
                new_records.append(record)
                self.records.append(record)
                self.id_to_index[paper.id] = len(self.records) - 1
        
        # Rebuild FAISS index
        self._rebuild_index()
        
        # Save to disk
        self._save_store()
        
        logger.info(f"Added {len(new_records)} new papers to embedding store")
    
    def _rebuild_index(self) -> None:
        """Rebuild FAISS index from current records"""
        if not self.records:
            return
        
        import faiss
        
        # Create new index
        embedding_dim = len(self.records[0].embedding)
        self.index = faiss.IndexFlatIP(embedding_dim)
        
        # Add all embeddings
        embeddings_matrix = np.vstack([record.embedding for record in self.records])
        self.index.add(embeddings_matrix.astype('float32'))
    
    def _save_store(self) -> None:
        """Save embedding store to disk"""
        if not self.index or not self.records:
            return
        
        try:
            import faiss
            
            # Save FAISS index
            index_file = self.store_path / "index.faiss"
            faiss.write_index(self.index, str(index_file))
            
            # Save records
            records_file = self.store_path / "records.pkl"
            with open(records_file, 'wb') as f:
                pickle.dump(self.records, f)
            
            # Save metadata
            metadata_file = self.store_path / "metadata.json"
            metadata = {
                "total_papers": len(self.records),
                "embedding_dim": len(self.records[0].embedding) if self.records else 0,
                "last_updated": str(Path().cwd())
            }
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
        except Exception as e:
            logger.error(f"Failed to save embedding store: {e}")
    
    def search(self, query_embedding: np.ndarray, k: int = 20) -> List[Tuple[EmbeddingRecord, float]]:
        """Search for similar papers using cosine similarity"""
        if not self.index or not self.records:
            return []
        
        # Normalize query embedding for cosine similarity
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        
        # Search
        scores, indices = self.index.search(query_embedding, min(k, len(self.records)))
        
        # Return results with scores
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.records):
                results.append((self.records[idx], float(score)))
        
        return results
    
    def get_paper_by_id(self, paper_id: str) -> Optional[EmbeddingRecord]:
        """Get paper record by ID"""
        if paper_id in self.id_to_index:
            return self.records[self.id_to_index[paper_id]]
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get store statistics"""
        return {
            "total_papers": len(self.records),
            "embedding_dim": len(self.records[0].embedding) if self.records else 0,
            "store_path": str(self.store_path)
        }


def get_embedding_store() -> EmbeddingStore:
    """Get global embedding store instance"""
    global _embedding_store
    if '_embedding_store' not in globals():
        _embedding_store = EmbeddingStore()
    return _embedding_store


# Global instance
_embedding_store: Optional[EmbeddingStore] = None
