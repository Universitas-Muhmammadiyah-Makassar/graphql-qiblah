import strawberry
from flask import Flask
from strawberry.flask.views import GraphQLView
from datetime import datetime, timedelta
import ephem
import math
from timezonefinder import TimezoneFinder
import pytz

# Fungsi utilitas yang ada tetap sama seperti sebelumnya
def dms_to_dd(degrees, minutes, seconds, direction):
    dd = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:
        dd *= -1
    return dd

def calculate_qibla_direction(lat1, long1, lat2, long2):
    delta_long = to_radians(long2 - long1)
    lat1_rad = to_radians(lat1)
    lat2_rad = to_radians(lat2)

    x = math.sin(delta_long) * math.cos(lat2_rad)
    y = math.cos(lat1_rad) * math.sin(lat2_rad) - (math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_long))
    qibla_direction = math.degrees(math.atan2(x, y))

    qibla_direction = (qibla_direction + 360) % 360

    return qibla_direction

def to_radians(degrees):
    return degrees * (math.pi / 180)

def get_timezone_name_and_offset(latitude, longitude, date_time):
    tf = TimezoneFinder()
    timezone_str = tf.timezone_at(lng=longitude, lat=latitude)
    if timezone_str is None:
        raise ValueError("Could not determine timezone for the provided coordinates.")
    
    timezone = pytz.timezone(timezone_str)
    utc_offset = timezone.utcoffset(date_time).total_seconds() / 3600

    if timezone_str == 'Asia/Makassar':
        timezone_name = timezone_str + ' - WITA'
    elif timezone_str == 'Asia/Jakarta':
        timezone_name = timezone_str + ' - WIB'
    elif timezone_str == 'Asia/Jayapura':
        timezone_name = timezone_str + ' - WIT'
    else:
        timezone_name = timezone_str
    
    return timezone_name, utc_offset

def parse_dms(dms_str):
    dms_str = dms_str.strip()
    parts = dms_str.split(' ')
    degrees = int(parts[0][:-1])
    minutes = int(parts[1][:-1])
    seconds = float(parts[2][:-1])
    direction = parts[3]
    return degrees, minutes, seconds, direction

# Definisikan Tipe Input untuk GraphQL
@strawberry.input
class LocationInput:
    latitude: str
    longitude: str
    datetime_str: str

# Definisikan Mutasi
@strawberry.type
class Mutation:
    @strawberry.mutation
    def calculate_solar(self, location_data: LocationInput) -> str:
        try:
            # Parse latitude and longitude strings
            lat_deg, lat_min, lat_sec, lat_dir = parse_dms(location_data.latitude)
            lon_deg, lon_min, lon_sec, lon_dir = parse_dms(location_data.longitude)
            
            observation_latitude = dms_to_dd(lat_deg, lat_min, lat_sec, lat_dir)
            observation_longitude = dms_to_dd(lon_deg, lon_min, lon_sec, lon_dir)

            # Parse datetime string
            date_time = datetime.strptime(location_data.datetime_str, '%Y/%m/%d %H:%M:%S')
            timezone_name, timezone_offset = get_timezone_name_and_offset(observation_latitude, observation_longitude, date_time)

            utc_time = date_time - timedelta(hours=timezone_offset)
            local_time = date_time

            observer = ephem.Observer()
            observer.lat = str(observation_latitude)
            observer.lon = str(observation_longitude)
            observer.elevation = 8
            observer.date = utc_time.strftime('%Y/%m/%d %H:%M:%S')

            sun = ephem.Sun(observer)
            solar_azimuth = sun.az * 180 / math.pi
            solar_elevation = sun.alt * 180 / math.pi

            shadow_azimuth = (solar_azimuth + 180) % 360

            kaaba_lat_dms = [21, 25, 21.2, 'N']
            kaaba_long_dms = [39, 49, 34.2, 'E']
            kaaba_lat = dms_to_dd(*kaaba_lat_dms)
            kaaba_long = dms_to_dd(*kaaba_long_dms)
            qibla_direction = calculate_qibla_direction(observation_latitude, observation_longitude, kaaba_lat, kaaba_long)

            shadow_azimuth_difference = abs(shadow_azimuth - qibla_direction)
            shadow_azimuth_difference = min(shadow_azimuth_difference, 360 - shadow_azimuth_difference)

            sun_azimuth_difference = abs(solar_azimuth - qibla_direction)
            sun_azimuth_difference = min(sun_azimuth_difference, 360 - sun_azimuth_difference)

            result = f"""
            Local Time: {local_time.strftime('%Y/%m/%d %H:%M:%S')} ({timezone_name})
            UTC Time: {utc_time.strftime('%Y/%m/%d %H:%M:%S')}
            Qibla Direction: {qibla_direction:.2f}° from the North
            Solar Elevation: {solar_elevation:.2f}°
            Solar Azimuth: {solar_azimuth:.2f}°
            Shadow Azimuth: {shadow_azimuth:.2f}°
            Solar Azimuth and Qibla Difference: {sun_azimuth_difference:.2f}°
            Shadow Azimuth and Qibla Difference: {shadow_azimuth_difference:.2f}°
            """
            return result.strip()

        except Exception as e:
            return f"Error: {str(e)}"

# Definisikan Query
@strawberry.type
class Query:
    hello: str = "Hello World"

# Buat skema
schema = strawberry.Schema(query=Query, mutation=Mutation)

# Inisialisasi Flask
app = Flask(__name__)
app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql_view", schema=schema))

if __name__ == "__main__":
    app.run(debug=True)
