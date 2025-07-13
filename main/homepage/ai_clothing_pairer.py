""" "python module to generate clothing pair suggestions using DALL·E and CLIP"""

import os
from datetime import datetime

import openai
import requests
import torch
from django.conf import settings
from PIL import Image
from transformers import CLIPModel, CLIPProcessor

# ==== Setup ====
API_KEY = """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"""

client = openai.OpenAI(api_key=API_KEY)

# Create output dir
OUTPUT_BASE_DIR = os.path.join(settings.MEDIA_ROOT, "paired_outfits")
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# List of possible clothing classes
CLOTHING_CATEGORIES = [
    "t-shirt",
    "shirt",
    "jeans",
    "skirt",
    "dress",
    "jacket",
    "blazer",
    "sweater",
    "hoodie",
    "shorts",
]

# Load CLIP model + processor (only once)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained(
    "openai/clip-vit-base-patch32", use_fast=False
)

# Map from clothing type to pairing prompts
PAIRINGS = {
    "shirt": [
        "a stylish pair of jeans",
        "a light jacket",
        "a brown blazer",
        "khaki chinos",
    ],
    "t-shirt": ["denim shorts", "a windbreaker", "cargo pants", "a varsity jacket"],
    "jeans": [
        "a fitted t-shirt",
        "a leather jacket",
        "white sneakers",
        "a casual hoodie",
    ],
    "dress": ["a light scarf", "a pair of heels", "a cute handbag", "a bolero jacket"],
    "skirt": ["a crop top", "a buttoned blouse", "a cardigan", "a fashionable belt"],
    "jacket": [
        "a pair of jeans",
        "a cotton shirt",
        "a turtleneck sweater",
        "leather gloves",
    ],
    "hoodie": ["joggers", "sneakers", "a denim jacket", "a baseball cap"],
    "blazer": ["dress pants", "a silk blouse", "oxford shoes", "a statement necklace"],
    "shorts": ["a tank top", "a bucket hat", "a summer shirt", "flip flops"],
    "sweater": ["corduroy pants", "a wool scarf", "ankle boots", "a trench coat"],
}


# ----- Classify clothing item using CLIP -----
def classify_clothing(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(
        text=CLOTHING_CATEGORIES, images=image, return_tensors="pt", padding=True
    )
    with torch.no_grad():
        outputs = clip_model(**inputs)
        logits_per_image = outputs.logits_per_image
        probs = logits_per_image.softmax(dim=1)
        best_idx = probs.argmax().item()
        best_label = CLOTHING_CATEGORIES[best_idx]
    print(f"[INFO] CLIP identified this as a: {best_label}")
    return best_label


# ----- Generate image using DALL·E -----
def generate_dalle_image(prompt, output_path):
    print(f"[INFO] Generating image for: {prompt}")
    try:
        response = client.images.generate(
            model="dall-e-3",  # or "dall-e-2"
            prompt=prompt,
            n=1,
            size="1024x1024",  # or "512x512" for dall-e-2
        )
        image_url = response.data[0].url
        image_data = Image.open(requests.get(image_url, stream=True).raw)
        image_data.save(output_path)
        print(f"[INFO] Saved to: {output_path}")
    except Exception as e:
        print(f"[ERROR] Failed to generate image: {e}")


# ----- Generate pair suggestions -----
def suggest_pairs(image_path):
    clothing_type = classify_clothing(image_path)
    pair_prompts = PAIRINGS.get(clothing_type, ["a coordinating fashion item"])
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for idx, item in enumerate(pair_prompts):
        # prompt = f"Image of a {item} that complements a {clothing_type} in the style of a ecommerce website product photo"
        prompt = f"A high-resolution product photo of a {item}, isolated on a plain white background, studio lighting, no mannequin, no model, no face, professional catalog image"
        OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, clothing_type)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        OUTPUT_DIR = os.path.join(OUTPUT_DIR, f"{timestamp}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, f"{item.replace(' ', '_')}.png")
        generate_dalle_image(prompt, output_file)


# ====== Entry point ======
if __name__ == "__main__":
    import argparse

    import requests

    parser = argparse.ArgumentParser(
        description="Generate clothing pair suggestions with DALL·E and CLIP"
    )
    parser.add_argument("image_path", help="Path to input clothing image")
    args = parser.parse_args()

    suggest_pairs(args.image_path)
