import os
from datetime import datetime
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from diffusers import StableDiffusionPipeline
import torch

# === Settings ===
OUTPUT_BASE_DIR = "paired_outfits_local"
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# === Load CLIP model ===
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32", use_fast=False)

# === Load Stable Diffusion (GPU) ===
pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16
).to("cuda")
pipe.safety_checker = lambda images, **kwargs: (images, [False] * len(images))  # disable NSFW filter

# === Clothing categories ===
CLOTHING_CATEGORIES = [
    "t-shirt", "shirt", "jeans", "skirt", "dress", "jacket",
    "blazer", "sweater", "hoodie", "shorts"
]

# === Pairing prompts ===
PAIRINGS = {
    "shirt": ["a stylish pair of jeans", "a light jacket", "a brown blazer", "khaki chinos"],
    "t-shirt": ["denim shorts", "a windbreaker", "cargo pants", "a varsity jacket"],
    "jeans": ["a fitted t-shirt", "a leather jacket", "white sneakers", "a casual hoodie"],
    "dress": ["a light scarf", "a pair of heels", "a cute handbag", "a bolero jacket"],
    "skirt": ["a crop top", "a buttoned blouse", "a cardigan", "a fashionable belt"],
    "jacket": ["a pair of jeans", "a cotton shirt", "a turtleneck sweater", "leather gloves"],
    "hoodie": ["joggers", "sneakers", "a denim jacket", "a baseball cap"],
    "blazer": ["dress pants", "a silk blouse", "oxford shoes", "a statement necklace"],
    "shorts": ["a tank top", "a bucket hat", "a summer shirt", "flip flops"],
    "sweater": ["corduroy pants", "a wool scarf", "ankle boots", "a trench coat"]
}

# === Classify clothing using CLIP ===
def classify_clothing(image_path):
    image = Image.open(image_path).convert("RGB")
    inputs = clip_processor(text=CLOTHING_CATEGORIES, images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        outputs = clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)
        best_idx = probs.argmax().item()
    best_label = CLOTHING_CATEGORIES[best_idx]
    print(f"[CLIP] Classified as: {best_label}")
    return best_label

# === Generate image using Stable Diffusion ===
def generate_image(prompt, output_path):
    print(f"[GEN] Prompt: {prompt}")
    image = pipe(prompt, num_inference_steps=30).images[0]
    image.save(output_path)
    print(f"[✔] Saved: {output_path}")

# === Suggest pairs ===
def suggest_pairs(image_path):
    clothing_type = classify_clothing(image_path)
    pair_items = PAIRINGS.get(clothing_type, ["a matching fashion item"])
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for idx, item in enumerate(pair_items):
        full_prompt = f"Image of a {item} that complements a {clothing_type} in the style of a ecommerce website product photo. No faces visible."
        OUTPUT_DIR = os.path.join(OUTPUT_BASE_DIR, clothing_type)
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        OUTPUT_DIR = os.path.join(OUTPUT_DIR, f"{timestamp}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        output_file = os.path.join(OUTPUT_DIR, f"{item}.png")
        generate_image(full_prompt, output_file)

# === Entry point ===
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Suggest clothing items using CLIP + Stable Diffusion")
    parser.add_argument("image_path", help="Path to input image of a clothing item")
    args = parser.parse_args()

    suggest_pairs(args.image_path)
