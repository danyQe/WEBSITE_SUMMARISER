import numpy as np
from typing import Dict, List, Union
from sentence_transformers import SentenceTransformer
import faiss
import json

class WebDataVectorizer:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize vectorization pipeline
        
        Args:
            model_name (str): Sentence transformer model for embedding generation
        """
        # Load pre-trained sentence transformer model
        self.embedding_model = SentenceTransformer(model_name)
        
        # Initialize FAISS index for efficient similarity search
        self.faiss_index = None
    
    def preprocess_text(self, text: Union[str, List[str]]) -> List[str]:
        """
        Preprocess text for vectorization
        
        Args:
            text (str or List[str]): Text to preprocess
        
        Returns:
            List[str]: Cleaned and processed text
        """
        if isinstance(text, str):
            text = [text]
        
        # Basic text cleaning
        cleaned_text = [
            ' '.join(t.lower().split())  # Normalize whitespace
            for t in text
            if t and len(t) > 10  # Filter out very short texts
        ]
        
        return cleaned_text
    
    def extract_vectorizable_content(self, extracted_data: Dict) -> Dict:
        """
        Extract and organize vectorizable content from scraped website data
        
        Args:
            extracted_data (Dict): Extracted website data
        
        Returns:
            Dict: Structured vectorizable content
        """
        vectorizable_content = {
            'metadata': [],
            'paragraphs': [],
            'headings': [],
            'links': []
        }
        
        # Iterate through extracted pages
        for url, page_data in extracted_data.get('extracted_data', {}).items():
            # Extract metadata text
            for key, value in page_data.get('metadata', {}).items():
                if isinstance(value, str):
                    vectorizable_content['metadata'].append(f"{key}: {value}")
            
            # Extract paragraphs
            paragraphs = page_data.get('text_content', {}).get('paragraphs', [])
            vectorizable_content['paragraphs'].extend(paragraphs)
            
            # Extract headings
            for heading_level, headings in page_data.get('text_content', {}).get('headings', {}).items():
                vectorizable_content['headings'].extend(headings)
            
            # Extract link texts
            links = page_data.get('links', [])
            vectorizable_content['links'].extend(links)
        
        return vectorizable_content
    
    def generate_embeddings(self, content: Dict) -> Dict:
        """
        Generate embeddings for different content types
        
        Args:
            content (Dict): Vectorizable content
        
        Returns:
            Dict: Embeddings for different content types
        """
        embeddings = {}
        
        for content_type, texts in content.items():
            # Preprocess texts
            cleaned_texts = self.preprocess_text(texts)
            
            if cleaned_texts:
                # Generate embeddings
                embeddings[content_type] = {
                    'texts': cleaned_texts,
                    'vectors': self.embedding_model.encode(cleaned_texts),
                    'dimension': self.embedding_model.get_sentence_embedding_dimension()
                }
        
        return embeddings
    
    def create_faiss_index(self, embeddings: Dict):
        """
        Create FAISS index for efficient similarity search
        
        Args:
            embeddings (Dict): Generated embeddings
        """
        # Combine all embeddings
        all_vectors = np.concatenate([
            embedding['vectors'] 
            for embedding in embeddings.values() 
            if 'vectors' in embedding
        ])
        
        # Create FAISS index
        dimension = all_vectors.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(all_vectors)
    
    def similarity_search(self, query: str, top_k: int = 5):
        """
        Perform similarity search on the vectorized content
        
        Args:
            query (str): Search query
            top_k (int): Number of top similar results to return
        
        Returns:
            List: Top similar results
        """
        if self.faiss_index is None:
            raise ValueError("FAISS index not created. Generate embeddings first.")
        
        # Embed query
        query_vector = self.embedding_model.encode([query])[0]
        
        # Perform similarity search
        distances, indices = self.faiss_index.search(
            np.array([query_vector]), top_k
        )
        
        return indices[0]
    
    def vectorize_website_data(self, extracted_data: Dict):
        """
        Complete vectorization pipeline
        
        Args:
            extracted_data (Dict): Website extraction data
        
        Returns:
            Dict: Vectorized website data
        """
        # Extract vectorizable content
        vectorizable_content = self.extract_vectorizable_content(extracted_data)
        
        # Generate embeddings
        embeddings = self.generate_embeddings(vectorizable_content)
        
        # Create FAISS index for similarity search
        self.create_faiss_index(embeddings)
        
        return {
            'vectorizable_content': vectorizable_content,
            'embeddings': embeddings
        }

def main():
    # Load previously extracted website data
    with open('website.json', 'r') as f:
        extracted_data = json.load(f)
    
    # Initialize vectorizer
    vectorizer = WebDataVectorizer()
    
    # Vectorize website data
    vectorized_data = vectorizer.vectorize_website_data(extracted_data)
    
    # Example similarity search
    query = "Find content related to machine learning"
    similar_indices = vectorizer.similarity_search(query)
    
    print("Vectorization complete!")
    print(f"Similarity search results for '{query}': {similar_indices}")

if __name__ == '__main__':
    main()