import os
import glob
from PIL import Image
from sentence_transformers import SentenceTransformer, util
import argparse

class SemanticSearch:
    def __init__(self, image_model_name='clip-ViT-B-32', text_model_name='all-MiniLM-L6-v2'):
        print(f"Loading image model {image_model_name}...")
        self.image_model = SentenceTransformer(image_model_name)
        print(f"Loading text model {text_model_name}...")
        self.text_model = SentenceTransformer(text_model_name)
        print("Models loaded.")
        
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
        self.text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json'}
        self.indexed_files = []
        self.image_embeddings = []
        self.text_embeddings = []

    def index_files(self, root_dir):
        print(f"Indexing files in {root_dir}...")
        image_paths = []
        text_paths = []
        
        for root, dirs, files in os.walk(root_dir):
            for file in files:
                filepath = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                if ext in self.image_extensions:
                    image_paths.append(filepath)
                elif ext in self.text_extensions:
                    text_paths.append(filepath)

        # Process Images
        if image_paths:
            print(f"Found {len(image_paths)} images. Generating embeddings...")
            images = []
            valid_image_paths = []
            for img_path in image_paths:
                try:
                    images.append(Image.open(img_path))
                    valid_image_paths.append(img_path)
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
            
            if images:
                img_emb = self.image_model.encode(images, convert_to_tensor=True)
                self.image_embeddings.extend(img_emb)
                self.indexed_files.extend([{'path': p, 'type': 'image'} for p in valid_image_paths])

        # Process Text
        if text_paths:
            print(f"Found {len(text_paths)} text files. Generating embeddings...")
            texts = []
            valid_text_paths = []
            for txt_path in text_paths:
                try:
                    with open(txt_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000) 
                        if content.strip():
                            texts.append(content)
                            valid_text_paths.append(txt_path)
                except Exception as e:
                    print(f"Error reading text {txt_path}: {e}")
            
            if texts:
                txt_emb = self.text_model.encode(texts, convert_to_tensor=True)
                self.text_embeddings.extend(txt_emb)
                self.indexed_files.extend([{'path': p, 'type': 'text'} for p in valid_text_paths])

        print(f"Indexed {len(self.image_embeddings)} images and {len(self.text_embeddings)} text files.")


    def search(self, query, top_k=5):
        print(f"Searching for: {query}")
        results = []

        # 1. Search Images with CLIP
        if self.image_embeddings:
            # Encode query with CLIP Text Encoder
            query_emb_clip = self.image_model.encode(query, convert_to_tensor=True)
            
            # Stack image embeddings
            import torch
            if isinstance(self.image_embeddings, list):
                if len(self.image_embeddings) > 0:
                     all_img_embs = torch.stack(self.image_embeddings) if isinstance(self.image_embeddings[0], torch.Tensor) else torch.tensor(self.image_embeddings)
                else:
                    all_img_embs = None
            else:
                 all_img_embs = self.image_embeddings
            
            if all_img_embs is not None:
                cos_scores = util.cos_sim(query_emb_clip, all_img_embs)[0]
                top_results = torch.topk(cos_scores, k=min(top_k, len(self.image_embeddings)))
                
                # Retrieve matching files (need to filter indexed_files for images only)
                # To make this easier, we should have stored them separately or indexed them
                # A quick fix: self.indexed_files stores ALL. The order of self.image_embeddings corresponds to 'type'=='image' entries in indexed_files?
                # No, that's risky. Let's filter first.
                
                # RE-Scan indexed_files to find images
                image_files = [f for f in self.indexed_files if f['type'] == 'image']
                
                for score, idx in zip(top_results[0], top_results[1]):
                    results.append((image_files[idx]['path'], score.item(), 'image'))

        # 2. Search Text with MiniLM
        if self.text_embeddings:
            # Encode query with MiniLM
            query_emb_text = self.text_model.encode(query, convert_to_tensor=True)
            
            # Stack text embeddings
            import torch
            if isinstance(self.text_embeddings, list):
                if len(self.text_embeddings) > 0:
                     all_txt_embs = torch.stack(self.text_embeddings) if isinstance(self.text_embeddings[0], torch.Tensor) else torch.tensor(self.text_embeddings)
                else:
                    all_txt_embs = None
            else:
                 all_txt_embs = self.text_embeddings
            
            if all_txt_embs is not None:
                cos_scores = util.cos_sim(query_emb_text, all_txt_embs)[0]
                top_results = torch.topk(cos_scores, k=min(top_k, len(self.text_embeddings)))
                
                text_files = [f for f in self.indexed_files if f['type'] == 'text']
                
                for score, idx in zip(top_results[0], top_results[1]):
                    results.append((text_files[idx]['path'], score.item(), 'text'))

        # Sort combined results by score (descending)
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Semantic Search Tool for Files")
    parser.add_argument("directory", help="Directory to search in")
    parser.add_argument("--query", "-q", help="Search query", required=True)
    args = parser.parse_args()

    searcher = SemanticSearch()
    searcher.index_files(args.directory)
    results = searcher.search(args.query)
    
    print("\nResults:")
    for res in results:
        print(res)
