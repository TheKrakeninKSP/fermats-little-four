import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import requests
import json
from django.conf import settings
import requests
import time
import json
from urllib.parse import quote
import random
import re

class ClothingClassifier:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Use HuggingFace transformers instead of clip-by-openai for PyTorch 2.7.1 compatibility
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
        # Clothing types and colors for classification
        self.clothing_types = [
            "t-shirt", "shirt", "blouse", "sweater", "hoodie", "jacket", "coat",
            "dress", "skirt", "pants", "jeans", "shorts", "leggings", "suit",
            "blazer", "cardigan", "tank top", "polo shirt", "button-up shirt"
        ]
        
        self.colors = [
            "black", "white", "gray", "blue", "red", "green", "yellow", "orange",
            "purple", "pink", "brown", "beige", "navy", "maroon", "olive", "teal"
        ]
    
    def classify_clothing(self, image_path):
        """Classify clothing type and color using CLIP via transformers"""
        try:
            image = Image.open(image_path).convert('RGB')
            
            # Classify clothing type
            type_texts = [f"a {clothing_type}" for clothing_type in self.clothing_types]
            
            # Process inputs
            inputs = self.processor(
                text=type_texts, 
                images=image, 
                return_tensors="pt", 
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=1)
                
            clothing_type = self.clothing_types[probs.argmax().item()]
            
            # Classify color
            color_texts = [f"a {color} clothing item" for color in self.colors]
            
            # Process inputs for color classification
            color_inputs = self.processor(
                text=color_texts, 
                images=image, 
                return_tensors="pt", 
                padding=True
            )
            
            # Move to device
            color_inputs = {k: v.to(self.device) for k, v in color_inputs.items()}
            
            with torch.no_grad():
                color_outputs = self.model(**color_inputs)
                color_logits = color_outputs.logits_per_image
                color_probs = color_logits.softmax(dim=1)
                
            clothing_color = self.colors[color_probs.argmax().item()]
            
            return clothing_type, clothing_color
            
        except Exception as e:
            print(f"Error in classification: {e}")
            return "shirt", "blue"  # Default fallback

class WalmartAPIService:
    def __init__(self):
        self.base_url = "https://www.walmart.com/search"
        
    def get_complementary_items(self, clothing_type, color):
        """Get complementary clothing items based on the classified item"""
        
        # Define complementary clothing rules
        complementary_rules = {
            "t-shirt": ["jeans", "shorts", "jacket", "cardigan"],
            "shirt": ["pants", "jeans", "blazer", "skirt"],
            "blouse": ["skirt", "pants", "jeans", "blazer"],
            "sweater": ["jeans", "pants", "skirt"],
            "hoodie": ["jeans", "shorts", "sweatpants"],
            "jacket": ["t-shirt", "shirt", "jeans", "pants"],
            "dress": ["jacket", "cardigan", "blazer", "coat"],
            "skirt": ["blouse", "shirt", "sweater", "blazer"],
            "pants": ["shirt", "blouse", "sweater", "t-shirt"],
            "jeans": ["t-shirt", "shirt", "sweater", "blouse"],
            "shorts": ["t-shirt", "tank top", "shirt"],
        }

        complementary_color_rules = {
            "black": ["white", "gray", "red", "beige", "gold", "silver"],
            "white": ["black", "navy", "red", "pastel", "denim", "beige"],
            "gray": ["black", "white", "pink", "burgundy", "blue", "mustard"],
            "navy": ["white", "beige", "yellow", "red", "gray"],
            "red": ["black", "white", "navy", "beige", "denim"],
            "blue": ["white", "gray", "beige", "tan", "yellow", "orange"],
            "light blue": ["white", "gray", "tan", "navy", "peach", "cream"],
            "green": ["white", "brown", "beige", "navy", "black"],
            "olive": ["white", "tan", "black", "cream", "rust"],
            "yellow": ["navy", "white", "gray", "denim", "olive"],
            "mustard": ["navy", "white", "gray", "burgundy", "olive"],
            "beige": ["white", "black", "navy", "olive", "brown", "rust"],
            "brown": ["white", "beige", "green", "orange", "tan"],
            "tan": ["white", "navy", "brown", "olive", "black"],
            "pink": ["white", "gray", "beige", "light blue", "burgundy"],
            "peach": ["white", "cream", "light blue", "olive"],
            "cream": ["white", "peach", "olive", "brown", "pink"],
            "purple": ["black", "gray", "white", "cream", "yellow"],
            "burgundy": ["white", "gray", "beige", "mustard", "pink"],
            "orange": ["navy", "white", "brown", "gray", "olive"],
            "denim": ["white", "gray", "black", "red", "mustard", "pink"],
            "pastel": ["white", "cream", "light gray", "denim", "beige"],
            "gold": ["black", "white", "cream", "burgundy"],
            "silver": ["black", "white", "gray", "navy"],
        }

        
        # Get complementary items
        complementary_types = complementary_rules.get(clothing_type, ["shirt", "pants"])
        complementary_colors = complementary_color_rules.get(color, ["blue", "red", "black"])
        
        all_items = []
        
        for indx, comp_type in enumerate(complementary_types[:5]):  # Get 5 complementary types
            item = self.search_walmart_items(comp_type, complementary_colors[indx])
            if item:
                all_items.append(item)
            
        return all_items[:5]  # Return top 5 items

    def search_walmart_items(self, item_type, color):
        """Search Walmart for clothing items with real product data and Google Images fallback"""
        
        # Clean inputs
        item_type = item_type.strip()
        color = color.strip()
        search_query = f"{color} {item_type}"
        
        print(f"Searching for: {search_query}")
        
        # Try to get real product data first
        product = get_walmart_product_data(search_query)
        
        if product:
            print(f"Found real product: {product['name']}")
            return product
        
        # If no real product found, create enhanced fallback with Google Images
        print("No real product found, creating enhanced fallback...")
        return create_enhanced_fallback(color, item_type, search_query)

def get_walmart_product_data(search_query):
    """Get actual product data from Walmart"""
    
    # Try the most reliable endpoint first
    encoded_query = quote(search_query)
    
    # This endpoint often works better for actual product data
    url = f"https://www.walmart.com/search/api/preso?query={encoded_query}&cat_id=5438&page=1&prg=desktop"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Referer': 'https://www.walmart.com/',
        'Origin': 'https://www.walmart.com',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Cache-Control': 'no-cache',
        'x-apollo-operation-name': 'Search',
        'x-latency-trace': '1'
    }
    
    try:
        time.sleep(random.uniform(1, 2))
        response = requests.get(url, headers=headers, timeout=15)
        
        print(f"Walmart API Status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Try to extract product data
                product = extract_walmart_product(data, search_query)
                if product:
                    return product
                    
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                
        elif response.status_code == 403:
            print("Access forbidden - trying alternative approach")
            return try_alternative_walmart_search(search_query)
            
        elif response.status_code == 429:
            print("Rate limited - waiting and retrying")
            time.sleep(3)
            return try_alternative_walmart_search(search_query)
            
    except Exception as e:
        print(f"Walmart API error: {e}")
    
    return None

def try_alternative_walmart_search(search_query):
    """Try alternative Walmart search methods"""
    
    # Try mobile API (often less restricted)
    mobile_url = f"https://www.walmart.com/m/search/api/preso?query={quote(search_query)}&cat_id=5438"
    
    mobile_headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
        'Accept': 'application/json',
        'Referer': 'https://www.walmart.com/'
    }
    
    try:
        time.sleep(1)
        response = requests.get(mobile_url, headers=mobile_headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            product = extract_walmart_product(data, search_query)
            if product:
                return product
                
    except Exception as e:
        print(f"Mobile API failed: {e}")
    
    # Try scraping search results page (last resort)
    return scrape_walmart_search_page(search_query)

def scrape_walmart_search_page(search_query):
    """Scrape the search results page for product data"""
    
    search_url = f"https://www.walmart.com/search?q={quote(search_query)}&cat_id=5438"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        time.sleep(1)
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Look for JSON data in the HTML
            html_content = response.text
            
            # Try to find embedded JSON data
            json_pattern = r'window\.__WML_REDUX_INITIAL_STATE__\s*=\s*({.+?});'
            match = re.search(json_pattern, html_content, re.DOTALL)
            
            if match:
                try:
                    json_data = json.loads(match.group(1))
                    product = extract_from_redux_state(json_data, search_query)
                    if product:
                        return product
                except json.JSONDecodeError:
                    pass
            
            # Alternative: Look for product data in script tags
            script_pattern = r'<script[^>]*>.*?"items":\s*\[([^\]]+)\]'
            matches = re.findall(script_pattern, html_content, re.DOTALL)
            
            for match in matches:
                try:
                    items_json = f'[{match}]'
                    items = json.loads(items_json)
                    if items and len(items) > 0:
                        return create_product_from_scraped_data(items[0], search_query)
                except json.JSONDecodeError:
                    continue
                    
    except Exception as e:
        print(f"Scraping failed: {e}")
    
    return None

def extract_walmart_product(data, search_query):
    """Extract product from Walmart API response"""
    
    items = []
    
    # Try different possible data structures
    paths_to_try = [
        ['results', 'items'],
        ['items'],
        ['products'],
        ['data', 'search', 'searchResult', 'itemStacks', 0, 'items'],
        ['props', 'pageProps', 'initialData', 'searchResult', 'itemStacks', 0, 'items'],
        ['searchResult', 'itemStacks', 0, 'items']
    ]
    
    for path in paths_to_try:
        try:
            current = data
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                elif isinstance(current, list) and isinstance(key, int) and len(current) > key:
                    current = current[key]
                else:
                    current = None
                    break
            
            if current and isinstance(current, list) and len(current) > 0:
                items = current
                print(f"Found {len(items)} items using path: {' -> '.join(map(str, path))}")
                break
                
        except Exception as e:
            print(f"Path {path} failed: {e}")
            continue
    
    if not items:
        print("No items found in response")
        return None
    
    # Get the first item
    first_item = items[0]
    print(f"First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else 'Not a dict'}")
    
    # Extract product details
    product_id = get_nested_value(first_item, ['usItemId', 'itemId', 'id', 'offerId'])
    product_name = get_nested_value(first_item, ['name', 'title', 'displayName'])
    
    if not product_name:
        print("No product name found")
        return None
    
    # Extract price
    price = extract_price_from_item(first_item)
    
    # Extract image
    image_url = get_nested_value(first_item, [
        'image', 'thumbnailImage', 'imageUrl', 'thumbnail', 
        'imageInfo', 'thumbnailUrl', 'primaryImage'
    ])
    
    # Create product URL
    product_url = create_product_url(product_id, product_name, search_query)
    
    return {
        "itemId": product_id or f"walmart_{hash(product_name) % 100000}",
        "name": product_name,
        "salePrice": price,
        "thumbnailImage": image_url or get_google_image(search_query),
        "productUrl": product_url,
        "categoryPath": get_nested_value(first_item, ['categoryPath', 'category'], 'Clothing'),
        "rating": get_nested_value(first_item, ['averageRating', 'rating', 'customerRating'], 0),
        "reviewCount": get_nested_value(first_item, ['numberOfReviews', 'reviewCount', 'numReviews'], 0),
        "availability": get_nested_value(first_item, ['availabilityStatus', 'availability'], 'Available'),
        "source": "walmart_real_data"
    }

def extract_from_redux_state(redux_data, search_query):
    """Extract product from Redux state data"""
    
    try:
        # Navigate through Redux state structure
        search_data = redux_data.get('search', {})
        search_result = search_data.get('searchResult', {})
        item_stacks = search_result.get('itemStacks', [])
        
        if item_stacks and len(item_stacks) > 0:
            items = item_stacks[0].get('items', [])
            if items and len(items) > 0:
                return extract_walmart_product({'items': items}, search_query)
                
    except Exception as e:
        print(f"Redux extraction failed: {e}")
    
    return None

def get_google_image(search_query):
    """Get first image URL from Google Images search (Unofficial, may break if Google layout changes)"""
    
    search_url = "https://www.google.com/search"
    params = {
        'q': search_query,
        'tbm': 'isch',
        'tbs': 'isz:m'  # Medium size images
    }
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive'
    }

    try:
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        html = response.text

        patterns = [
            r'"ou":"([^"]+)"',  # Most common image pattern (original image)
            r'"imgurl":"([^"]+)"',  # Alternate format
            r'data-src="([^"]+)"',
            r'src="([^"]+)".*?class="[^"]*image[^"]*"',
            r'https://[^"]*\.(?:jpg|jpeg|png|webp)[^"]*'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html)
            for match in matches:
                if (match.startswith('http') and
                    any(match.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']) and
                    'google' not in match.lower() and
                    'logo' not in match.lower() and
                    len(match) > 50):
                    print(f"Found Google image: {match[:100]}...")
                    return match

    except Exception as e:
        print(f"Google Images search failed: {e}")

    # Fallback
    print("Failed to get Google image, using placeholder")
    return "https://i5.walmartimages.com/dfw/4ff9c6c9-52/k2-_15938eb7-8e42-4f7a-b8d7-c1d6e1b5a0d5.v1.jpg"

def create_enhanced_fallback(color, item_type, search_query):
    """Create enhanced fallback with Google Images"""
    
    search_url = f"https://www.walmart.com/search?q={quote(search_query)}&cat_id=5438"
    
    return {
        "itemId": f"fallback_{hash(search_query) % 100000}",
        "name": f"{color.title()} {item_type.title()}",
        "salePrice": 0,
        "thumbnailImage": get_google_image(search_query),
        "productUrl": search_url,
        "categoryPath": "Clothing",
        "rating": 0,
        "reviewCount": 0,
        "availability": "Search Required",
        "source": "enhanced_fallback"
    }

def get_nested_value(data, keys, default=None):
    """Safely get nested dictionary values"""
    if not isinstance(keys, list):
        keys = [keys]
    
    for key in keys:
        try:
            if isinstance(data, dict) and key in data and data[key] is not None:
                return data[key]
        except Exception:
            continue
    
    return default

def extract_price_from_item(item):
    """Extract price from item with multiple fallbacks"""
    
    price_paths = [
        ['priceInfo', 'currentPrice', 'price'],
        ['priceInfo', 'currentPrice'],
        ['price', 'current'],
        ['salePrice'],
        ['currentPrice'],
        ['priceRange', 'minPrice'],
        ['pricing', 'currentPrice'],
        ['offerPrice']
    ]
    
    for path in price_paths:
        try:
            current = item
            for key in path:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    current = None
                    break
            
            if current is not None:
                if isinstance(current, (int, float)):
                    return current
                elif isinstance(current, str):
                    # Extract numeric value from string
                    price_match = re.search(r'[\d.]+', current)
                    if price_match:
                        return float(price_match.group())
        except Exception:
            continue
    
    return 0

def create_product_url(product_id, product_name, search_query):
    """Create product URL"""
    
    if product_id and product_name:
        # Create URL-safe name
        url_name = re.sub(r'[^a-zA-Z0-9\-]', '-', product_name.lower())
        url_name = re.sub(r'-+', '-', url_name).strip('-')
        return f"https://www.walmart.com/ip/{url_name}/{product_id}"
    
    # Fallback to search
    return f"https://www.walmart.com/search?q={quote(search_query)}&cat_id=5438"

def create_product_from_scraped_data(item_data, search_query):
    """Create product from scraped HTML data"""
    
    return {
        "itemId": item_data.get('itemId', f"scraped_{hash(search_query) % 100000}"),
        "name": item_data.get('name', search_query.title()),
        "salePrice": item_data.get('price', 0),
        "thumbnailImage": item_data.get('image', get_google_image(search_query)),
        "productUrl": item_data.get('url', f"https://www.walmart.com/search?q={quote(search_query)}&cat_id=5438"),
        "categoryPath": "Clothing",
        "rating": item_data.get('rating', 0),
        "reviewCount": item_data.get('reviews', 0),
        "availability": "Available",
        "source": "scraped_data"
    }

# Test function
def test_search(item_type="shirt", color="blue"):
    """Test the search function"""
    
    class MockSelf:
        pass
    
    mock_self = MockSelf()
    result = search_walmart_items(mock_self, item_type, color)
    
    print(f"\n=== Search Results for '{color} {item_type}' ===")
    print(f"Name: {result['name']}")
    print(f"Price: ${result['salePrice']}")
    print(f"Image: {result['thumbnailImage'][:80]}...")
    print(f"URL: {result['productUrl']}")
    print(f"Source: {result['source']}")
    print(f"Rating: {result['rating']} ({result['reviewCount']} reviews)")
    
    return result

# Example usage:
# result = test_search("hoodie", "red")
# result = test_search("jeans", "black")