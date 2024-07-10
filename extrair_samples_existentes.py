import json
import os
from PIL import Image

def check_file_existence(sample_data_file, image_folder):
    samples_with_existence = []  # List to store objects whose images exist
    
    # Load sample data
    with open(sample_data_file, 'r') as f:
        sample_data = json.load(f)
    count = 0
    # Iterate through sample data
    for data in sample_data:
        filename = data.get('filename', None)
        if filename:
            filepath = os.path.join(image_folder, filename)
            if os.path.exists(filepath):
                samples_with_existence.append(data)
                count += 1
            if(count == 10):
                print(filepath)
                img = Image.open(filepath)
                img.show()
    print(f"Existem {count} ficheiros")
    
# Example usage
if __name__ == "__main__":
    # Paths to the JSON files
    sample_data_file = "sample_data.json"

    # Folder containing image files
    image_folder = r"C:\Users\ricar\Downloads\nuimages-v1.0-all-samples"

    # Check file existence and write to a new file
    check_file_existence(sample_data_file, image_folder)
