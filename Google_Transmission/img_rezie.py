from PIL import Image
import io

def download_image_from_drive(url, folder_path, name, timestamp):
    try:
        file_id = extract_file_id(url)
        download_url = f"https://drive.google.com/uc?id={file_id}"
        response = requests.get(download_url)

        name = sanitize_filename(name)
        timestamp = timestamp.replace(' ', '').replace('/', '').replace(':', '')

        file_name = os.path.join(folder_path, f"{name}_{timestamp}.jpg")
        
        # Open the image using PIL
        img = Image.open(io.BytesIO(response.content))
        
        # Resize the image
        img_resized = img.resize((320, 260), Image.LANCZOS)
        
        # Save the resized image
        img_resized.save(file_name, 'JPEG')

        print(f"Downloaded, resized, and saved file to '{file_name}'")
        return file_name

    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error downloading image from {url}: {e}")
        print(traceback.format_exc())
        file_name = os.path.join(folder_path, f"{name}_{timestamp}.jpg")
        create_placeholder_image(file_name)
        return file_name