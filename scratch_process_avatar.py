import os
import sys
from rembg import remove
from PIL import Image

def main():
    input_path = r"C:\Users\USER\.gemini\antigravity\brain\f7172566-b33a-409f-aae4-c821ba49a151\media__1784476134488.jpg"
    output_dir = r"c:\Users\USER\OneDrive\Desktop\My projects\My Portfolio\DevBuddyAI\assets"
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "avatar_transparent.png")
    
    print(f"Loading image from: {input_path}")
    if not os.path.exists(input_path):
        print("Error: Input image not found!")
        sys.exit(1)
        
    try:
        input_image = Image.open(input_path)
        print("Removing background using rembg...")
        output_image = remove(input_image)
        output_image.save(output_path)
        print(f"Success! Saved transparent avatar to: {output_path}")
    except Exception as e:
        print(f"Error processing image: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
