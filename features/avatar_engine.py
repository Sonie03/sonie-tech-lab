import os
from PIL import Image, ImageDraw

class AvatarEngine:
    def __init__(self, assets_dir):
        self.assets_dir = assets_dir
        self.base_avatar_path = os.path.join(assets_dir, "avatar_transparent.png")
        self.composited_avatar_path = os.path.join(assets_dir, "avatar_composited.png")

    def process_avatar(self, input_path: str, output_path: str) -> bool:
        """Remove background from input_path and save transparent PNG to output_path."""
        try:
            from rembg import remove
            from PIL import Image as PILImage
            img = PILImage.open(input_path)
            result = remove(img)
            result.save(output_path)
            return True
        except Exception as e:
            print(f"[AvatarEngine] Background removal failed: {e}")
            return False

        
    def generate_custom_avatar(self, config):
        """
        config dictionary keys:
        - hairstyle: 'none', 'spiky', 'curly', 'cap'
        - hair_color: hex or rgb tuple
        - clothes: 'none', 'devops_hoodie', 'tshirt', 'suit'
        - clothes_color: hex or rgb tuple
        - accessory: 'none', 'glasses', 'headphones'
        - pose: 'normal', 'holding_water'
        - face_x, face_y, face_scale: offsets for face accessories/hair
        - body_x, body_y, body_scale: offsets for clothes
        """
        if not os.path.exists(self.base_avatar_path):
            # Create a simple generic head if no user photo exists
            base_img = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
            draw = ImageDraw.Draw(base_img)
            draw.ellipse([100, 100, 300, 300], fill=(220, 180, 150, 255)) # simple face
            base_img.save(self.base_avatar_path)
        else:
            base_img = Image.open(self.base_avatar_path).convert("RGBA")
            
        # Resize to standard workspace size
        base_img = base_img.resize((400, 400), Image.Resampling.LANCZOS)
        
        # Create a new transparent composite canvas
        canvas = Image.new("RGBA", (400, 400), (0, 0, 0, 0))
        canvas.alpha_composite(base_img)
        
        draw = ImageDraw.Draw(canvas)
        
        # Get offset/scale configurations (fallback to defaults if not set)
        fx = int(config.get("face_x", 0))
        fy = int(config.get("face_y", 0))
        fs = float(config.get("face_scale", 1.0))
        
        bx = int(config.get("body_x", 0))
        by = int(config.get("body_y", 0))
        bs = float(config.get("body_scale", 1.0))
        
        # 1. Overlay Hairstyle
        hair = config.get("hairstyle", "none")
        h_color = config.get("hair_color", (50, 30, 20, 255))
        if hair == "spiky":
            # Procedural spiky hair drawn on top of the head
            hair_path = [
                (140 + fx, 120 + fy), (160 + fx, 90 + fy), (180 + fx, 110 + fy),
                (200 + fx, 80 + fy), (220 + fx, 110 + fy), (240 + fx, 90 + fy),
                (260 + fx, 120 + fy), (280 + fx, 100 + fy), (290 + fx, 140 + fy),
                (270 + fx, 160 + fy), (130 + fx, 160 + fy)
            ]
            draw.polygon(hair_path, fill=h_color)
        elif hair == "curly":
            # Procedural curly hair bubbles
            for dx, dy in [(-10, 0), (0, -10), (10, -10), (20, 0), (30, 10), (-20, 10)]:
                cx, cy = 200 + fx + dx, 120 + fy + dy
                draw.ellipse([cx-30, cy-30, cx+30, cy+30], fill=h_color)
        elif hair == "cap":
            # Cute blue cap
            draw.chord([120 + fx, 90 + fy, 280 + fx, 210 + fy], 180, 360, fill=(0, 120, 215, 255)) # Cap body
            draw.rounded_rectangle([140 + fx, 140 + fy, 320 + fx, 160 + fy], radius=5, fill=(0, 90, 180, 255)) # Visor
            
        # 2. Overlay Clothes
        clothes = config.get("clothes", "none")
        c_color = config.get("clothes_color", (0, 120, 215, 255)) # DevBuddy Blue
        if clothes == "devops_hoodie":
            # Hoodie shape covering the torso
            hoodie_path = [
                (120 + bx, 320 + by), (280 + bx, 320 + by),
                (350 + bx, 400 + by), (50 + bx, 400 + by)
            ]
            draw.polygon(hoodie_path, fill=c_color)
            # Draw hoodie pocket
            draw.rounded_rectangle([150 + bx, 360 + by, 250 + bx, 400 + by], radius=10, fill=(0, 90, 180, 255))
            # Draw drawstrings
            draw.line([180 + bx, 320 + by, 180 + bx, 355 + by], fill=(255, 255, 255, 255), width=3)
            draw.line([220 + bx, 320 + by, 220 + bx, 355 + by], fill=(255, 255, 255, 255), width=3)
        elif clothes == "tshirt":
            tshirt_path = [
                (130 + bx, 320 + by), (270 + bx, 320 + by),
                (330 + bx, 370 + by), (310 + bx, 400 + by),
                (270 + bx, 380 + by), (270 + bx, 400 + by),
                (130 + bx, 400 + by), (130 + bx, 380 + by),
                (90 + bx, 400 + by), (70 + bx, 370 + by)
            ]
            draw.polygon(tshirt_path, fill=c_color)
        elif clothes == "suit":
            # Suit jacket
            draw.polygon([(110+bx, 320+by), (290+bx, 320+by), (350+bx, 400+by), (50+bx, 400+by)], fill=(40, 40, 40, 255))
            # Shirt V neck
            draw.polygon([(170+bx, 320+by), (230+bx, 320+by), (200+bx, 360+by)], fill=(255, 255, 255, 255))
            # Red tie
            draw.polygon([(195+bx, 335+by), (205+bx, 335+by), (210+bx, 380+by), (200+bx, 390+by), (190+bx, 380+by)], fill=(220, 50, 50, 255))

        # 3. Overlay Accessories
        acc = config.get("accessory", "none")
        if acc == "glasses":
            # Draw cool round glasses
            draw.ellipse([150 + fx, 180 + fy, 195 + fx, 225 + fy], outline=(50, 50, 50, 255), width=3)
            draw.ellipse([205 + fx, 180 + fy, 250 + fx, 225 + fy], outline=(50, 50, 50, 255), width=3)
            # Bridge
            draw.line([195 + fx, 202 + fy, 205 + fx, 202 + fy], fill=(50, 50, 50, 255), width=3)
            # Sides
            draw.line([130 + fx, 202 + fy, 150 + fx, 202 + fy], fill=(50, 50, 50, 255), width=2)
            draw.line([250 + fx, 202 + fy, 270 + fx, 202 + fy], fill=(50, 50, 50, 255), width=2)
        elif acc == "headphones":
            # Headband
            draw.arc([130 + fx, 120 + fy, 270 + fx, 260 + fy], 180, 360, fill=(30, 30, 30, 255), width=8)
            # Left cup
            draw.rounded_rectangle([120 + fx, 175 + fy, 140 + fx, 225 + fy], radius=5, fill=(0, 120, 215, 255))
            # Right cup
            draw.rounded_rectangle([260 + fx, 175 + fy, 280 + fx, 225 + fy], radius=5, fill=(0, 120, 215, 255))

        # 4. Pose (e.g. Water Glass overlay)
        pose = config.get("pose", "normal")
        if pose == "holding_water":
            # Draw hand holding a translucent blue water glass
            # Glass body
            draw.polygon([(260, 280), (300, 280), (290, 340), (270, 340)], fill=(0, 180, 255, 150))
            # Water level
            draw.polygon([(263, 295), (297, 295), (290, 337), (273, 337)], fill=(0, 100, 255, 180))
            # Hand holding
            draw.rounded_rectangle([240, 295, 280, 315], radius=5, fill=(220, 180, 150, 255))

        # Save composited image
        canvas.save(self.composited_avatar_path)
        return self.composited_avatar_path
