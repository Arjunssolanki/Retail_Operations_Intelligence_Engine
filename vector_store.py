import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
from logger_config import get_logger
import torch.nn as nn 

logger = get_logger("vector_store")

class ChromaStorageEngine:
    def __init__(self):
        logger.info("Initializing vector repository connection space.")
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="retail_intelligence_space",
            embedding_function=self.emb_fn
        )

    def populate_index(self, records: List[Dict[str, Any]]):
        if not records:
            return
            
        logger.info(f"Upserting {len(records)} structural mappings into Chroma DB.")
        
        ids = [item["id"] for item in records]
        texts = [item["text"] for item in records]
        metadatas = [item["metadata"] for item in records]
        
        batch_limit = 100
        for cursor in range(0, len(ids), batch_limit):
            self.collection.upsert(
                ids=ids[cursor:cursor+batch_limit],
                documents=texts[cursor:cursor+batch_limit],
                metadatas=metadatas[cursor:cursor+batch_limit]
            )
        logger.info("Vector space indexing completed successfully.")

    def semantic_search(self, query: str, n_results: int = 5) -> List[str]:
        logger.info(f"Querying vector database for: '{query}'")
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results.get("documents", [[]])
