
import os
import sys
import glob
import chromadb
import ollama
import argparse

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DIR = os.path.join(BASE_DIR, '../src/lib/pesonaldata/DBmakedused/chunks')
CHROMA_PATH = os.path.join(BASE_DIR, '../src/data/chroma_db')
COLLECTION_NAME = 'limitless_logs'
OLLAMA_EMBED_MODEL = os.environ.get('OLLAMA_EMBED_MODEL', 'nomic-embed-text')

CATEGORIES = ['Fact', 'Thought', 'Experience']

def generate_embedding(text):
    try:
        response = ollama.embeddings(model=OLLAMA_EMBED_MODEL, prompt=text)
        return response.get('embedding', [])
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return []

def split_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += (chunk_size - overlap)
    return chunks

def main():
    print(f"Connecting to Chroma at {CHROMA_PATH}...")
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Handle Reset
    if os.environ.get('RESET_COLLECTION') == 'true':
        try:
            client.delete_collection(name=COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'")
        except:
            pass
    
    collection = client.get_or_create_collection(name=COLLECTION_NAME, metadata={"description": "Personal data logs"})
    print(f"Collection '{COLLECTION_NAME}' ready.")

    # Exclusion Patterns
    exclude_env = os.environ.get('EXCLUDE_PATTERN')
    exclude_patterns = []
    if exclude_env:
        exclude_patterns = [p.strip().lower() for p in exclude_env.split(',') if p.strip()]
        if exclude_patterns:
            print(f"Exclusion Patterns Active: {exclude_patterns}")

    total_processed = 0
    total_skipped = 0

    for category in CATEGORIES:
        category_dir = os.path.join(SOURCE_DIR, category)
        if not os.path.exists(category_dir):
            print(f"Category directory missing: {category_dir}")
            continue
        
        files = [f for f in os.listdir(category_dir) if f.endswith('.txt')]
        print(f"Processing {category}: {len(files)} files found.")
        
        for file in files:
            # Check exclusion
            if any(p in file.lower() for p in exclude_patterns):
                total_skipped += 1
                continue
            
            file_path = os.path.join(category_dir, file)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if not content.strip():
                continue
                
            chunks = split_text(content)
            
            ids = []
            embeddings = []
            metadatas = []
            documents = []
            
            for i, chunk in enumerate(chunks):
                embedding = generate_embedding(chunk)
                if not embedding:
                    continue
                
                chunk_id = f"{category}_{file}_{i}"
                ids.append(chunk_id)
                embeddings.append(embedding)
                metadatas.append({
                    "source": file,
                    "category": category,
                    "chunk_index": i
                })
                documents.append(chunk)
            
            if ids:
                collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents
                )
                print(".", end="", flush=True)
            
            total_processed += 1
            
        print(f"\nFinished {category}.")

    print(f"\nIngestion complete.")
    print(f"Processed: {total_processed}")
    print(f"Skipped: {total_skipped}")

if __name__ == "__main__":
    main()
