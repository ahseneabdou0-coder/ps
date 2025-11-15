from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_data(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()
    if not exif_data:
        return {}
    exif = {}
    for tag_id, value in exif_data.items():
        tag = TAGS.get(tag_id, tag_id)
        if tag == "GPSInfo":
            gps_data = {}
            for t in value:
                sub_tag = GPSTAGS.get(t, t)
                gps_data[sub_tag] = value[t]
            exif["GPSInfo"] = gps_data
        else:
            exif[tag] = value
    return exif

def get_time(exif):
    return exif.get("DateTimeOriginal")

def get_coordinates(exif):
    gps_info = exif.get("GPSInfo")
    if not gps_info:
        return None

    def convert_to_degrees(value):
        d, m, s = value

        def to_float(x):
            if isinstance(x, tuple):
                return float(x[0]) / float(x[1])
            return float(x)

        return to_float(d) + to_float(m) / 60 + to_float(s) / 3600

    if "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
        lat = convert_to_degrees(gps_info["GPSLatitude"])
        lon = convert_to_degrees(gps_info["GPSLongitude"])

        if gps_info.get("GPSLatitudeRef") == "S":
            lat = -lat
        if gps_info.get("GPSLongitudeRef") == "W":
            lon = -lon

        
        lat = f"{lat:.6f}"
        lon = f"{lon:.6f}"

        return (lat, lon)
    return None

def extract_metadata(image_path):
    exif = get_exif_data(image_path)
    time = get_time(exif)
    coords = get_coordinates(exif)
    return {
        "time": time,
        "coordinates": coords,
    }