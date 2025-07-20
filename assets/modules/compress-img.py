from PIL import Image
import glob
import json

# open json
def open_json(file_path):
    try:
        # Open the JSON file for reading
        with open(file_path, 'r', encoding='utf-8') as file:
            # Load the JSON data
            data = json.load(file)
    
        return data
    
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Function to resize and convert an image to WebP
def convert_to_webp(input_image_name, sizes, compression_quality=100):
    # Get the input image path
    input_image_path = glob.glob(f"{input_image_name}.*")[0]

    """Converts the image to WebP format in multiple sizes"""
    with Image.open(input_image_path) as img:
        for size in sizes:
            # Resize the image while maintaining aspect ratio
            img_resized = img.resize((size, int(size * img.height / img.width)))
            # Save the resized image in WebP format
            webp_output_path = f"{input_image_name}-{size}w.webp"
            img_resized.save(webp_output_path, "WEBP", quality=compression_quality)
            print(f"Saved {webp_output_path} with size {size}px width")

# Define desired sizes for WebP images (widths)
mem_img_sizes = [200, 400, 600, 800]
glf_img_sizes = [200, 400, 600, 800, 1200, 1600, 2000]
lazy_img_sizes = [20]

# Convert images to WebP format
for ele in ['mem', 'glf'][:]:
    data_list = open_json(f'../src/{ele}.json')

    for data in data_list:
        print(data['imgPath'])
        img_name = data['imgPath'].split('/')[-1].split('.')[0]
        convert_to_webp(f"../{ele}/{img_name}", globals()[f'{ele}_img_sizes'], compression_quality=70)
        convert_to_webp(f"../{ele}/{img_name}", globals()['lazy_img_sizes'], compression_quality=10)