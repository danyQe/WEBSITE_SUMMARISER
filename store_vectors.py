import chromadb
from chromadb.config import Settings
import uuid
import numpy as np
from typing import Dict, List, Any

class ChromaDBVectorStore:
    def __init__(self, 
                 collection_name: str = 'web_scraped_content', 
                 persist_directory: str = './chroma_storage'):
        """
        Initialize ChromaDB Vector Storage
        
        Args:
            collection_name (str): Name of the collection to store vectors
            persist_directory (str): Directory to persist the database
        """
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persist_directory)
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
    
    def prepare_vectors(self, 
                        embeddings: Dict[str, Dict], 
                        extracted_data: Dict[str, Any]) -> List[Dict]:
        """
        Prepare vectors for storage with metadata
        
        Args:
            embeddings (Dict): Generated embeddings
            extracted_data (Dict): Original extracted web data
        
        Returns:
            List[Dict]: Prepared vector documents
        """
        vector_documents = []
        
        # Iterate through different content types
        for content_type, embedding_data in embeddings.items():
            texts = embedding_data.get('texts', [])
            vectors = embedding_data.get('vectors', [])
            
            for idx, (text, vector) in enumerate(zip(texts, vectors)):
                # Generate unique ID
                doc_id = str(uuid.uuid4())
                
                # Prepare metadata
                metadata = {
                    'content_type': content_type,
                    'text': text,
                    # Add additional context from original data if needed
                    'source': f'web_scrape_{content_type}_{idx}'
                }
                
                vector_documents.append({
                    'id': doc_id,
                    'embedding': vector.tolist(),
                    'metadata': metadata,
                    'document': text
                })
        
        return vector_documents
    
    def store_vectors(self, 
                      embeddings: Dict[str, Dict], 
                      extracted_data: Dict[str, Any]):
        """
        Store vectors in ChromaDB
        
        Args:
            embeddings (Dict): Generated embeddings
            extracted_data (Dict): Original extracted web data
        """
        # Prepare vectors
        vector_documents = self.prepare_vectors(embeddings, extracted_data)
        
        # Batch insert vectors
        for batch_start in range(0, len(vector_documents), 100):
            batch = vector_documents[batch_start:batch_start+100]
            
            # Extract components for ChromaDB insertion
            ids = [doc['id'] for doc in batch]
            embeddings = [doc['embedding'] for doc in batch]
            metadatas = [doc['metadata'] for doc in batch]
            documents = [doc['document'] for doc in batch]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
        
        print(f"Stored {len(vector_documents)} vectors in ChromaDB")
    
    def query_vectors(self, 
                      query_text: str, 
                      n_results: int = 5, 
                      include: List[str] = None):
        """
        Query vectors in the database
        
        Args:
            query_text (str): Query string
            n_results (int): Number of results to return
            include (List[str]): What to include in results
        
        Returns:
            Dict: Query results
        """
        # Default include options
        if include is None:
            include = ['documents', 'distances', 'metadatas']
        
        # Perform query
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            include=include
        )
        
        return results
    
    def delete_vectors(self, ids: List[str] = None, filter: Dict = None):
        """
        Delete vectors from the collection
        
        Args:
            ids (List[str]): Specific vector IDs to delete
            filter (Dict): Metadata filter for deletion
        """
        if ids:
            self.collection.delete(ids=ids)
        elif filter:
            self.collection.delete(where=filter)
        else:
            raise ValueError("Provide either ids or filter for deletion")
    
    def get_collection_count(self) -> int:
        """
        Get the number of vectors in the collection
        
        Returns:
            int: Number of vectors
        """
        return self.collection.count()

def main():
    from sentence_transformers import SentenceTransformer
    import json
    
    # Load previously extracted and vectorized website data
    with open('vectorized_website_data.json', 'r') as f:
        vectorized_data = json.load(f)
    
    # Initialize ChromaDB Vector Store
    chroma_store = ChromaDBVectorStore(
        collection_name='web_content_vectors',
        persist_directory='./chroma_storage'
    )
    
    # Store vectors
    chroma_store.store_vectors(
        embeddings=vectorized_data['embeddings'],
        extracted_data=vectorized_data.get('extracted_data', {})
    )
    
    # Example query
    query = "Find information about machine learning"
    results = chroma_store.query_vectors(query, n_results=3)
    
    # Print results
    print("Query Results:")
    for i, (doc, distance, metadata) in enumerate(zip(
        results['documents'][0], 
        results['distances'][0], 
        results['metadatas'][0]
    ), 1):
        print(f"{i}. Distance: {distance}")
        print(f"   Content Type: {metadata.get('content_type', 'N/A')}")
        print(f"   Text: {doc}\n")
    
    # Get total vector count
    print(f"Total vectors stored: {chroma_store.get_collection_count()}")

if __name__ == '__main__':
    main()