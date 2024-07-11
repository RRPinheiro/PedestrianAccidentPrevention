import os
import random
import shutil

def move_random_files(source_image_folder, source_text_folder, destination_image_folder, destination_text_folder, num_files):
    # Create the destination folders if they don't exist
    os.makedirs(destination_image_folder, exist_ok=True)
    os.makedirs(destination_text_folder, exist_ok=True)

    # Get a list of all image files in the source image folder
    all_image_files = os.listdir(source_image_folder)

    # Select a random subset of image files
    random_image_files = random.sample(all_image_files, num_files)

    # Move the selected image files to the destination image folder
    for image_file_name in random_image_files:
        # Move image file
        source_image_path = os.path.join(source_image_folder, image_file_name)
        destination_image_path = os.path.join(destination_image_folder, image_file_name)
        shutil.move(source_image_path, destination_image_path)

        # Move corresponding text file from the source text folder to the destination text folder
        text_file_name = os.path.splitext(image_file_name)[0] + ".txt"
        source_text_path = os.path.join(source_text_folder, text_file_name)
        destination_text_path = os.path.join(destination_text_folder, text_file_name)
        if os.path.exists(source_text_path):
            shutil.move(source_text_path, destination_text_path)

# Example usage
if __name__ == "__main__":
    # Source folders containing images and corresponding text files
    source_image_folder = r""
    source_text_folder = r""

    # Destination folders to move the selected files
    destination_image_folder = ""
    destination_text_folder = ""

    # Number of random files to select
    num_files = 10000

    # Move random files to the destination folders
    move_random_files(source_image_folder, source_text_folder, destination_image_folder, destination_text_folder, num_files)
