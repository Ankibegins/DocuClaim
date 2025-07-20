from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
import asyncio

class EmbeddingManager:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
    
    async def get_embeddings(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text(s)"""
        try:
            if isinstance(texts, str):
                texts = [texts]
            
            # Run embedding generation in a thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None, self.model.encode, texts
            )
            
            return embeddings
            
        except Exception as e:
            raise Exception(f"Error generating embeddings: {str(e)}")
    
    async def get_single_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embeddings = await self.get_embeddings(text)
        return embeddings[0]
    
    def get_dimension(self) -> int:
        """Get the embedding dimension"""
        return self.dimension 