import os
import json
from pathlib import Path
from .url_fetcher import URLFetcher


def read_and_preprocess_files(input_dir: str) -> str:
    """
    Read and preprocess all files from the given directory.
    Also fetches content from any URLs found in the files.
    
    Args:
        input_dir (str): Path to the directory containing input files
        
    Returns:
        str: Combined content of all files with preprocessing and URL content
    """
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Directory not found: {input_dir}")
    
    combined_content = []
    all_text_content = ""  # Collect all text to scan for URLs later
    
    # Initialize URL fetcher
    url_fetcher = URLFetcher()
    
    # Get all files from the directory
    input_path = Path(input_dir)
    
    for file_path in input_path.rglob("*"):
        if file_path.is_file():
            print(f"🔍 Processing file: {file_path}")
            try:
                # Skip binary files and common non-text files
                if file_path.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.bin', '.exe']:
                    print(f"⏭️  Skipping binary file: {file_path}")
                    continue
                
                # Handle JSON files specially for better formatting
                if file_path.suffix.lower() == '.json':
                    print(f"📋 Processing JSON file: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as file:
                        json_data = json.load(file)
                        # Format JSON nicely for the AI to read
                        formatted_json = json.dumps(json_data, indent=2, ensure_ascii=False)
                        file_content = f"=== JSON FILE: {file_path.relative_to(input_path)} ===\n{formatted_json}\n"
                        combined_content.append(file_content)
                        all_text_content += formatted_json + "\n"
                        print(f"✅ JSON file processed: {len(formatted_json):,} characters")
                else:
                    # Handle regular text files
                    print(f"📄 Processing text file: {file_path}")
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read().strip()
                        if content:
                            file_content = f"=== FILE: {file_path.relative_to(input_path)} ===\n{content}\n"
                            combined_content.append(file_content)
                            all_text_content += content + "\n"
                            print(f"✅ Text file processed: {len(content):,} characters")
                        else:
                            print(f"⚠️  Text file is empty: {file_path}")
            except (UnicodeDecodeError, PermissionError, json.JSONDecodeError) as e:
                # Skip files that can't be read as text or invalid JSON
                print(f"Warning: Could not read file {file_path}: {e}")
                continue
    
    # Check for dedicated URLs file and fetch content from those URLs
    urls_file = input_path / "urls.txt"
    fetched_urls = []
    
    if urls_file.exists():
        print("🔍 Found urls.txt file, fetching content from specified URLs...")
        try:
            with open(urls_file, 'r', encoding='utf-8') as f:
                urls_content = f.read().strip()
            fetched_urls = url_fetcher.process_urls_from_text(urls_content, max_urls=10)
        except Exception as e:
            print(f"⚠️  Error reading urls.txt: {e}")
    else:
        print("ℹ️  No urls.txt file found. Create input/urls.txt to fetch content from specific URLs.")
    
    # Add fetched URL content to the combined content
    if fetched_urls:
        combined_content.append("\n=== CONTENT FETCHED FROM URLs ===\n")
        for url_data in fetched_urls:
            url_content = f"=== URL: {url_data['url']} ===\n"
            url_content += f"Title: {url_data['title']}\n"
            url_content += f"Content Type: {url_data['content_type']}\n"
            url_content += f"Content:\n{url_data['content'][:5000]}...\n"  # Limit content length
            if len(url_data['content']) > 5000:
                url_content += "[Content truncated - showing first 5000 characters]\n"
            combined_content.append(url_content)
        
        print(f"✅ Successfully fetched content from {len(fetched_urls)} URL(s)")
    else:
        print("ℹ️  No URLs found in input files")
    
    return "\n".join(combined_content) 