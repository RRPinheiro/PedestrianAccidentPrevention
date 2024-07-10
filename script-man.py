import json
import os

def generate_yolo_annotations(sample_existe_file, object_ann_file):
    with open(sample_existe_file, 'r') as f:
        sample_data = json.load(f)
        
    atributos = ['60346f6d0fcd4d9eadd6f64c77dd1e93', '8c92f43bdb7c4df399aac34068f08f0f', '963614d0532a4c6e946d303a94f40a3e']
    
    with open(object_ann_file, 'r') as f:
        object_ann = json.load(f)

    total_files = len(sample_data)
    print(f"{total_files} ficheiros")
    files_processed = 0

    yolo_folder = os.path.join(os.getcwd(), "yolo_annotations")
    os.makedirs(yolo_folder, exist_ok=True)

    for data in sample_data:
        filename = data.get('filename', None)
        if filename:
            image_name = os.path.splitext(os.path.basename(filename))[0]
            txt_filename = os.path.join(yolo_folder, image_name + ".txt")
            with open(txt_filename, 'w') as txt_file:
                for obj in object_ann:
                    if obj.get('sample_data_token') == data.get('token'):
                        attribute_tokens = obj.get('attribute_tokens', [])
                        if any(attr_token in attribute_tokens for attr_token in atributos):
                            bbox = obj.get('bbox')
                            width = bbox[2] - bbox[0]
                            height = bbox[3] - bbox[1]
                            img_width = data.get('width')
                            img_height = data.get('height')
                            x_center = (bbox[0] + bbox[2]) / (2 * img_width)
                            y_center = (bbox[1] + bbox[3]) / (2 * img_height)
                            width_norm = width / img_width
                            height_norm = height / img_height
                            txt_file.write(f"0 {x_center} {y_center} {width_norm} {height_norm}\n")
            files_processed += 1
            print(f"Processed {files_processed}/{total_files} files ({(files_processed/total_files)*100:.2f}%)")


if __name__ == "__main__":
    # Paths to the JSON files
    object_ann_file = "object_ann.json"
    sample_existe_file = "sample_existe.json"

    
    generate_yolo_annotations(sample_existe_file, object_ann_file)
