from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS
import os

# Function to get date_time data from a photo
def get_photo_date_time(photo):

    # Exif tags
    DATE_TIME_ORIGINAL = 36867
    DATE_TIME_DIGITIZED = 36868
    DATE_TIME = 306

    image = Image.open(photo)
    exif_data = image._getexif()

    for tag_id in (DATE_TIME_ORIGINAL, DATE_TIME_DIGITIZED, DATE_TIME):
        value = exif_data.get(tag_id)
        if value:
            return value

    # If tag not available, return date of last file modificaton
    timestamp = os.path.getmtime(photo)
    value = datetime.fromtimestamp(timestamp)
    return value

# Function to validate folder selection
def check_path():

    while True:

        path = input("Please enter the path to the folder containing your photos: ")

        # Path validation: Does the path exist?
        if not os.access(path, os.F_OK):
            print("\nThis path does not exist.\n")
            continue

        # Folder validation: Does the path lead to a folder?
        if not os.path.isdir(path):
            print("\nThis path does not lead to a folder.\n")
            continue

        # Folder validation: Confirm correct folder selected
        base_name = os.path.basename(path)

        while True:

            status = input(f"\nYou have selected: '{base_name}'. Do you want to proceed with photo organisation? Please enter 'y' or 'n'.\n")

            if status == "n" or status == "y":
                break

            print("\nInvalid input.\n")

        if status == "n":
            continue

        # Folder validation: check permissions
        try:
            os.listdir(path)

            temp_path = os.path.join(path, "temp_file.txt")
            with open(temp_path, "w") as temp:
                temp.write("test")

            renamed_path = os.path.join(path, "renamed_file.txt")
            os.rename(temp_path, renamed_path)

            os.remove(renamed_path)

        except PermissionError:
            print("\nYou do not have permission to modify this folder.\n")
            continue

        print("\nFolder confimred. Commencing photo organisation...\n")
        break

    return path

# Function to collect all photos from sub-directories
def collect_photos(path):

    photos = []

    extensions = [".jpg", ".jpeg", ".png", ".heic", ".gif", ".bmp", ".tiff"]

    with os.scandir(path) as directory:
        for entry in directory:
            if os.path.isdir(entry.path):
                photos.extend(collect_photos(entry.path))
            elif os.path.splitext(entry.name)[1].lower() in extensions:
                photos.append(entry.path)

    return photos

# Function to rename all photos
def rename_photos(photos):

    renamed_paths = []

    for photo in photos:

        value = get_photo_date_time(photo)

        # Convert to datetime object
        if isinstance(value, str):
            dt = datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
        else:
            dt = value

        #new name
        date = dt.strftime("%Y-%m-%d_%H-%M-%S")
        ext = os.path.splitext(photo)[1]
        new_name = f"{date}{ext}"
        # Old path
        folder = os.path.dirname(photo)
        # New path
        new_path = os.path.join(folder, new_name)

        # Rename
        os.rename(photo, new_path)

        renamed_paths.append((new_path, dt))

    return renamed_paths

# Function to move photos into new folders
def move_photos(renamed_paths, base_folder):

    for photo_path, dt in renamed_paths:

        # Build folder name: YYYY-MM
        folder_name = dt.strftime("%Y-%m")
        target_folder = os.path.join(base_folder, folder_name)

        # Create folder if missing
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)

        # Build destination path
        filename = os.path.basename(photo_path)
        destination = os.path.join(target_folder, filename)

        # Move the file
        os.rename(photo_path, destination)

path = check_path()
photos = collect_photos(path)

renamed_paths = rename_photos(photos)
move_photos(renamed_paths, path)

print("Photo organisation completed :)")