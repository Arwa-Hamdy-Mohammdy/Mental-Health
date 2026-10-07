"""
RAG Pipeline Module
Handles Knowledge Base loading, document chunking, vector embedding, and similarity search.
"""

import os
import glob
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from src.config import DATA_DIR, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RETRIEVAL

class MentalHealthRAG:
    def __init__(self, data_dir: str = DATA_DIR):
        self.data_dir = data_dir
        self.documents: List[Dict[str, str]] = []
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self.faiss_store = None
        self.use_faiss = False
        
        self.load_documents()
        self.create_chunks()
        self.build_index()

    def load_documents(self):
        """Loads all markdown and text documents from knowledge base directory."""
        self.documents = []
        if not os.path.exists(self.data_dir):
            return
            
        file_paths = glob.glob(os.path.join(self.data_dir, "*.md")) + glob.glob(os.path.join(self.data_dir, "*.txt"))
        for filepath in file_paths:
            filename = os.path.basename(filepath)
            title = filename.replace(".md", "").replace(".txt", "").replace("_", " ").title()
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            self.documents.append({
                "source": filename,
                "title": title,
                "content": content
            })

    def create_chunks(self, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
        """Splits documents into overlapping chunks with metadata."""
        self.chunks = []
        for doc in self.documents:
            text = doc["content"]
            lines = text.split("\n\n")
            
            current_chunk = ""
            for line in lines:
                if len(current_chunk) + len(line) <= chunk_size:
                    current_chunk += line + "\n\n"
                else:
                    if current_chunk.strip():
                        self.chunks.append({
                            "text": current_chunk.strip(),
                            "source": doc["source"],
                            "title": doc["title"]
                        })
                    current_chunk = line[-overlap:] + "\n\n" + line if len(line) > overlap else line + "\n\n"
                    
            if current_chunk.strip():
                self.chunks.append({
                    "text": current_chunk.strip(),
                    "source": doc["source"],
                    "title": doc["title"]
                })

    def build_index(self):
        """Builds vector index using FAISS if available or TF-IDF Cosine Similarity."""
        if not self.chunks:
            return

        # Attempt FAISS + Sentence Transformers if installed
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            from langchain_community.vectorstores import FAISS
            from langchain_core.documents import Document
            
            docs = [Document(page_content=c["text"], metadata={"source": c["source"], "title": c["title"]}) for c in self.chunks]
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
            self.faiss_store = FAISS.from_documents(docs, embeddings)
            self.use_faiss = True
            print("Successfully initialized FAISS Vector Store with SentenceTransformers.")
        except Exception as e:
            # Fallback to Scikit-Learn TF-IDF vectorizer
            print(f"FAISS/LangChain Embeddings not yet active ({e}). Using Scikit-Learn Vector Space index.")
            chunk_texts = [c["text"] for c in self.chunks]
            self.vectorizer = TfidfVectorizer(stop_words='english')
            self.tfidf_matrix = self.vectorizer.fit_transform(chunk_texts)
            self.use_faiss = False

    def retrieve(self, query: str, top_k: int = TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """Retrieves top-k relevant knowledge base chunks for a given user query."""
        if not self.chunks:
            return []

        if self.use_faiss and self.faiss_store:
            try:
                results = self.faiss_store.similarity_search_with_score(query, k=top_k)
                retrieved = []
                for doc, score in results:
                    retrieved.append({
                        "text": doc.page_content,
                        "source": doc.metadata.get("source", "Knowledge Base"),
                        "title": doc.metadata.get("title", "Resource"),
                        "score": float(score)
                    })
                return retrieved
            except Exception as e:
                print("FAISS search error, switching to vector space search:", e)

        # Fallback Vector Space Similarity Search
        if self.vectorizer and self.tfidf_matrix is not None:
            query_vec = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            top_indices = similarities.argsort()[::-1][:top_k]
            
            retrieved = []
            for idx in top_indices:
                if similarities[idx] > 0.05:
                    chunk = self.chunks[idx]
                    retrieved.append({
                        "text": chunk["text"],
                        "source": chunk["source"],
                        "title": chunk["title"],
                        "score": float(similarities[idx])
                    })
            return retrieved

        return []
