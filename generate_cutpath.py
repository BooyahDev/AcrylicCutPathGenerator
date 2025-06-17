import cv2
import numpy as np
import svgwrite
import sys
from skimage import measure
import base64
from io import BytesIO
from PIL import Image

def generate_cutpath(input_png, output_svg, offset=10):
    # Load image (BGRA or BGR)
    image = cv2.imread(input_png, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise FileNotFoundError(f"Image '{input_png}' not found.")

    height, width = image.shape[:2]

    # Handle alpha if available
    if image.shape[2] == 4:
        alpha = image[:, :, 3]
        _, binary = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)

    # Extract contours
    contours = measure.find_contours(binary, 0.5)

    # Draw filled shape for dilation
    mask = np.zeros(binary.shape, dtype=np.uint8)
    for contour in contours:
        pts = np.flip(np.round(contour).astype(np.int32), axis=1)  # Flip (row,col) -> (x,y)
        cv2.drawContours(mask, [pts], -1, 255, thickness=cv2.FILLED)

    # Dilate to create offset
    kernel_size = offset * 2 + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    dilated = cv2.dilate(mask, kernel, iterations=1)

    # Find final contours
    final_contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create SVG
    dwg = svgwrite.Drawing(output_svg, size=(f"{width}px", f"{height}px"))
    
    # Embed PNG image as base64
    with Image.open(input_png) as img:
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_b64 = base64.b64encode(buffered.getvalue()).decode()

    image_href = f"data:image/png;base64,{img_b64}"
    dwg.add(dwg.image(href=image_href, insert=(0, 0), size=(f"{width}px", f"{height}px")))

    # Add contours
    for cnt in final_contours:
        path_data = "M " + " L ".join(f"{p[0][0]},{p[0][1]}" for p in cnt) + " Z"
        dwg.add(dwg.path(d=path_data, fill="none", stroke="red", stroke_width=1))

    dwg.save()
    print(f"SVG saved to {output_svg}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("使い方: python generate_acrylic_cutpath.py <入力画像.png> <出力パス.svg> [オフセット(px)]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    offset = int(sys.argv[3]) if len(sys.argv) > 3 else 10

    generate_cutpath(input_file, output_file, offset)

