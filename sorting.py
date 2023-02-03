import os
import re
import piexif
import datetime
import shutil
import ffmpeg
from iso6709 import Location
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="geoapiExercises")
extensions = ('.jpg', '.jpeg', '.mov', '.dng')


def location_mov(file):
    try:
        loc_iso6709 = ffmpeg.probe(file)['format']['tags']['com.apple.quicktime.location.ISO6709']
        loc = Location(loc_iso6709)
        latitude, longitude = loc.lat.degrees, loc.lng.degrees
        if '-' in loc_iso6709.split('+')[0]:
            latitude = -latitude
        if '-' in loc_iso6709.split('+')[1]:
            longitude = -longitude
        return latitude, longitude
    except:
        return None


def location_jpg(file):
    try:
        exif_dict = piexif.load(file)
        coords = {
            'GPSLatitude': exif_dict["GPS"].get(piexif.GPSIFD.GPSLatitude),
            'GPSLatitudeRef': exif_dict["GPS"].get(piexif.GPSIFD.GPSLatitudeRef),
            'GPSLongitude': exif_dict["GPS"].get(piexif.GPSIFD.GPSLongitude),
            'GPSLongitudeRef': exif_dict["GPS"].get(piexif.GPSIFD.GPSLongitudeRef)
        }
        if coords:
            lat, lng = convert_raw_coords(coords)
            return lat, lng
        else:
            return None
    except:
        return None


def creation_time_mov(file):
    try:
        mov_datetime = ffmpeg.probe(file)['format']['tags']['com.apple.quicktime.creationdate']
        creation_time = datetime.datetime.strptime(mov_datetime, '%Y-%m-%dT%H:%M:%S%z')
        return creation_time
    except:
        return None


def creation_time_jpg(file):
    try:
        exif_dict = piexif.load(file)
        creation_time = datetime.datetime.strptime(exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal].decode(),
                                                   '%Y:%m:%d %H:%M:%S')
        return creation_time
    except:
        return None


def creation_time_heic(file):
    pass
    # TODO


def get_file_creation_time(file):
    creation_time = None
    if file.endswith(".jpg") or file.endswith(".jpeg") or file.endswith(".dng"):
        creation_time = creation_time_jpg(file)
    elif file.endswith(".HEIC") or file.endswith(".heic"):
        creation_time = creation_time_heic(file)
    elif file.endswith(".mov"):
        creation_time = creation_time_mov(file)

    if creation_time is None:
        match = re.search(r'(\d{4}-\d{2}-\d{2})', file)
        if match:
            date = match.group(0)
            creation_time = datetime.datetime.strptime(date, '%Y-%m-%d')
    return creation_time


def convert_raw_coords(gps_exif):
    # convert the rational tuples by dividing each (numerator, denominator) pair
    lat = [n / d for n, d in gps_exif['GPSLatitude']]
    lon = [n / d for n, d in gps_exif['GPSLongitude']]

    # now you have lat and lon, which are lists of [degrees, minutes, seconds]
    # from the formula above
    dd_lat = lat[0] + lat[1] / 60 + lat[2] / 3600
    dd_lon = lon[0] + lon[1] / 60 + lon[2] / 3600

    # if latitude ref is 'S', make latitude negative
    if gps_exif['GPSLatitudeRef'] == 'S':
        dd_lat = -dd_lat

    # if longitude ref is 'W', make longitude negative
    if gps_exif['GPSLongitudeRef'] == 'W':
        dd_lon = -dd_lon

    return (dd_lat, dd_lon)


def get_location_from_file(file):
    if (file.endswith(".jpg")
            or file.endswith(".jpeg")
            or file.endswith(".dng")):
        # or file.endswith(".heic") \
        # or file.endswith(".HEIC"):
        if location_jpg(file):
            lat, lng = location_jpg(file)
            return lat, lng
        else:
            # print("No location were found in ", file)
            return None

    elif file.endswith(".mov"):
        if location_mov(file):
            return location_mov(file)
        else:
            # print("No location were found in ", file)
            return None
    else:
        return None


def get_country_from_location(location):
    if location:
        lat, lng = location
        try:
            location = geolocator.reverse(f"{lat}, {lng}", exactly_one=True, language='en')
            country = location.raw['address'].get('country', None)
            return country
        except:
            return None
    else:
        return None


def sort_media_files(folder_path):
    for filename in os.listdir(folder_path):
        if not filename.endswith(extensions):
            continue

        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            creation_time = get_file_creation_time(file_path)
            location = get_location_from_file(file_path)

            if creation_time is None:
                print(f"{filename} - No creation date found in exif or file name")
                continue

            year, month = creation_time.strftime("%Y.%m").split('.')
            year_month = f"{year}.{month}"
            year_month_folder = os.path.join(folder_path, year_month)

            if location:
                country = get_country_from_location(location)
                if country:
                    country_folder = os.path.join(folder_path, f"{year_month} {country}")
                else:
                    country_folder = year_month_folder
            else:
                # if you want to print filename w/o location - uncomment the following line
                # print(f"{filename} - No location data found in exif or file name")
                country_folder = year_month_folder

            if not os.path.exists(country_folder):
                os.makedirs(country_folder)

            shutil.move(file_path, os.path.join(country_folder, filename))
            # if you want to print the processing of each file - uncomment the following line
            # print(f"{filename} - Creation date: {creation_time} - Folder: {country_folder}")


if __name__ == "__main__":
    subfolder_name = None
    subfolder_name = input("Enter the subfolder name: ")
    subfolder_name = subfolder_name or 'samples '
    folder_path = os.path.join(os.getcwd(), subfolder_name)
    if os.path.exists(folder_path):
        sort_media_files(folder_path)
    else:
        print(f"Subfolder '{subfolder_name}' not found.")
