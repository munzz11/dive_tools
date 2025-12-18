import csv
import os
import glob
import dive_tools as dt

csv_path = input('Enter the path to the CSV annotations file: ')
img_dir = input('Enter the path to the directory containing images: ')
path2labels = input('Enter the path to the labels directory: ')

# Get all image files from the directory and sort them
img_extensions = ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']
image_files = []
for ext in img_extensions:
    pattern = os.path.join(img_dir, ext)
    image_files.extend(glob.glob(pattern))

# Remove duplicates and sort
image_files = sorted(list(set(image_files)))

if not image_files:
    print(f"Error: No image files found in directory: {img_dir}")
    exit(1)

print(f"Found {len(image_files)} image files in directory")

# Create a mapping from frame number to image file
# Frame numbers in CSV are 0-indexed, so frame 0 = first image, frame 1 = second image, etc.
frame_to_image = {}
for idx, img_path in enumerate(image_files):
    frame_to_image[idx] = img_path

try:
    with open(csv_path, 'r') as csv_file:
        for line in csv_file:
            if line[0] != '#':
                data = dt.CSVData(line)
                # Get the image file for this frame number
                if data.frame not in frame_to_image:
                    print(f"Warning: Frame {data.frame} is out of range. Found {len(image_files)} images (frames 0-{len(image_files)-1})")
                    continue
                
                img_path = frame_to_image[data.frame]
                # Pass None to use the image filename directly for the label file
                data.make_labelfiles(img_path, path2labels, None)
except Exception as e:
    print(e)





