from PIL import Image, ImageDraw, ImageFont
import os

def create_icon():
    """Create a modern icon matching the widget's dark theme design"""
    
    # Create image with transparency
    size = 256
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    
    # Draw main circular background with gradient effect (dark slate like widget)
    # Outer circle - darker slate
    draw.ellipse([5, 5, size-5, size-5], fill=(15, 23, 42, 255))
    
    # Inner circle - lighter slate (gradient effect)
    inner_margin = 15
    draw.ellipse([inner_margin, inner_margin, size-inner_margin, size-inner_margin], 
                 fill=(30, 41, 59, 255))
    
    # Draw three colored arcs representing the three timers (like the gradient cards)
    import math
    
    # Green arc (Work time) - top right
    arc_width = 25
    for i in range(arc_width):
        alpha = int(255 * (1 - i/arc_width))
        draw.arc([40+i, 40+i, size-40-i, size-40-i], 
                start=-60, end=60, 
                fill=(16, 185, 129, alpha), width=3)
    
    # Orange arc (Leisure time) - bottom right  
    for i in range(arc_width):
        alpha = int(255 * (1 - i/arc_width))
        draw.arc([40+i, 40+i, size-40-i, size-40-i], 
                start=60, end=180, 
                fill=(245, 158, 11, alpha), width=3)
    
    # Blue arc (Total time) - left side
    for i in range(arc_width):
        alpha = int(255 * (1 - i/arc_width))
        draw.arc([40+i, 40+i, size-40-i, size-40-i], 
                start=180, end=300, 
                fill=(59, 130, 246, alpha), width=3)
    
    # Draw central play/activity symbol (modern triangle)
    triangle_size = 50
    triangle_x = center + 8
    triangle_y = center
    
    # Play triangle (represents activity tracking)
    points = [
        (triangle_x - triangle_size//3, triangle_y - triangle_size//2),
        (triangle_x - triangle_size//3, triangle_y + triangle_size//2),
        (triangle_x + triangle_size//2, triangle_y)
    ]
    draw.polygon(points, fill=(255, 255, 255, 255))
    
    # Add small accent circles for modern look
    accent_radius = 8
    # Top accent (green)
    draw.ellipse([center - accent_radius, 45 - accent_radius, 
                  center + accent_radius, 45 + accent_radius],
                 fill=(16, 185, 129, 255))
    
    # Bottom right accent (orange)
    angle_orange = math.radians(120)
    x_orange = center + 70 * math.cos(angle_orange)
    y_orange = center + 70 * math.sin(angle_orange)
    draw.ellipse([x_orange - accent_radius, y_orange - accent_radius,
                  x_orange + accent_radius, y_orange + accent_radius],
                 fill=(245, 158, 11, 255))
    
    # Bottom left accent (blue)
    angle_blue = math.radians(240)
    x_blue = center + 70 * math.cos(angle_blue)
    y_blue = center + 70 * math.sin(angle_blue)
    draw.ellipse([x_blue - accent_radius, y_blue - accent_radius,
                  x_blue + accent_radius, y_blue + accent_radius],
                 fill=(59, 130, 246, 255))
    
    # Save as ICO file (Windows icon)
    img.save('icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
    print("Modern icon created: icon.ico")
    
    # Also save as PNG for reference
    img.save('icon.png', format='PNG')
    print("Icon preview created: icon.png")

if __name__ == "__main__":
    create_icon()
