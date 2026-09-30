import os
import json
import argparse
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
import string
import time
from collections import Counter

class PersistentSearch:
    def __init__(self, index_file='index.json'):
        self.index_file = index_file
        self.index = {}
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        self.text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json'}
        
        # Load existing index if available
        if os.path.exists(self.index_file):
            print(f"Loading index from {self.index_file}...")
            try:
                with open(self.index_file, 'r') as f:
                    self.index = json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}. Starting fresh.")
                self.index = {}

        # Lazy load model
        self.u_processor = None
        self.u_model = None

    def _load_model(self):
        if self.u_model is None:
            print("Loading Captioning Model (BLIP)...")
            self.u_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            self.u_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            print("Model loaded.")

    def analyze_folder(self, root_dir):
        print(f"Analyzing files in {root_dir}...")
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                # specific logic to skip re-indexing if modified time hasn't changed? 
                # For simplicity, we just check existence. But we SHOULD update timestamp on re-scan if valid?
                # The user wants auto-delete > 30 days. If we just skip, the timestamp might get old.
                # So if we find it, let's update timestamp to keep it alive.
                
                if filepath in self.index:
                    self.index[filepath]['timestamp'] = time.time()
                    continue

                if ext in self.image_extensions:
                    self._analyze_image(filepath)
                elif ext in self.text_extensions:
                    self._analyze_text(filepath)
        
        self.save_index()

    def _analyze_image(self, filepath):
        self._load_model()
        try:
            raw_image = Image.open(filepath).convert('RGB')
            # conditional check for small images?
            
            inputs = self.u_processor(raw_image, return_tensors="pt")
            out = self.u_model.generate(**inputs)
            caption = self.u_processor.decode(out[0], skip_special_tokens=True)
            
            print(f"[IMAGE] {filepath} -> {caption}")
            
            # Extract keywords from caption
            keywords = [w.strip(string.punctuation).lower() for w in caption.split()]
            
            self.index[filepath] = {
                "type": "image",
                "caption": caption,
                "keywords": keywords,
                "timestamp": time.time()
            }
        except Exception as e:
            print(f"Error analyzing image {filepath}: {e}")

    def _analyze_text(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            # Simple keyword extraction: top most frequent words that are not too short
            words = [w.strip(string.punctuation).lower() for w in content.split()]
            words = [w for w in words if len(w) > 3]
            
            # Take top 50 common words + raw content snippet
            common = [w for w, c in Counter(words).most_common(50)]
            
            print(f"[TEXT] {filepath} -> indexed {len(common)} keywords")
            
            self.index[filepath] = {
                "type": "text",
                "keywords": common,
                "snippet": content[:200],
                "timestamp": time.time()
            }
            
        except Exception as e:
            print(f"Error analyzing text {filepath}: {e}")

    def prune_index(self, max_days=30):
        print("Pruning index...")
        now = time.time()
        max_seconds = max_days * 86400
        keys_to_delete = []
        
        for filepath, data in self.index.items():
            # If no timestamp (legacy), set it to now to avoid deletion
            if 'timestamp' not in data:
                data['timestamp'] = now
                continue
            
            if (now - data['timestamp']) > max_seconds:
                keys_to_delete.append(filepath)
        
        if keys_to_delete:
            print(f"Removing {len(keys_to_delete)} old entries.")
            for k in keys_to_delete:
                del self.index[k]
            self.save_index()
        else:
            print("No old entries found to prune.")


    def save_index(self):
        print(f"Saving index to {self.index_file}...")
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def search(self, query):
        print(f"Searching for key: '{query}'")
        query_words = [w.strip().lower() for w in query.split()]
        results = []
        
        for filepath, data in self.index.items():
            score = 0
            # Search in keywords
            for q in query_words:
                if any(q in k for k in data.get('keywords', [])):
                    score += 1
                if 'caption' in data and q in data['caption'].lower():
                    score += 2
                    
            if score > 0:
                results.append((filepath, score, data))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Persistent Semantic Search")
    subparsers = parser.add_subparsers(dest='command', required=True)
    
    # Analyze command
    parser_analyze = subparsers.add_parser('analyze', help='Scan folder and build index')
    parser_analyze.add_argument('directory', help='Directory to scan')
    
    # Search command
    parser_search = subparsers.add_parser('search', help='Search the index')
    parser_search.add_argument('query', help='Keyword to search')
    
    args = parser.parse_args()
    
    searcher = PersistentSearch()
    
    if args.command == 'analyze':
        searcher.analyze_folder(args.directory)
    elif args.command == 'search':
        results = searcher.search(args.query)
        print(f"\nFound {len(results)} matches:")
        for path, score, data in results:
            desc = data.get('caption', data.get('snippet', ''))
            print(f"- [{score}] {path}\n  {desc}")
