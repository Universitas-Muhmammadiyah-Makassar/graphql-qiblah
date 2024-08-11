import strawberry
from flask import Flask
from strawberry.flask.views import GraphQLView
from datetime import datetime, timedelta
import ephem
import math
from timezonefinder import TimezoneFinder
import pytz

# Fungsi untuk mengonversi DMS (Derajat, Menit, Detik) ke Derajat Desimal
def dms_to_decimal(degrees, minutes, seconds, direction):
    decimal = degrees + minutes / 60 + seconds / 3600
    if direction in ['S', 'W']:
        decimal *= -1  # Negatif untuk arah Selatan dan Barat
    return decimal

# Fungsi untuk mengonversi Derajat Desimal ke DMS
def to_dms(decimal):
    absolute = abs(decimal)
    degrees = math.floor(absolute)
    minutes_not_truncated = (absolute - degrees) * 60
    minutes = math.floor(minutes_not_truncated)
    seconds = (minutes_not_truncated - minutes) * 60
    return degrees, minutes, seconds

# Fungsi untuk menghitung arah Kiblat
def calculate_qibla_direction(lat1_dms, lon1_dms):
    # Koordinat Ka'bah dalam DMS
    lat2_dms = (21, 25, 21.2, 'N')
    lon2_dms = (39, 49, 34.2, 'E')

    # Konversi lokasi pengamatan ke derajat desimal
    lat1 = dms_to_decimal(*lat1_dms)
    lon1 = dms_to_decimal(*lon1_dms)

    # Konversi lokasi Ka'bah ke derajat desimal
    lat2 = dms_to_decimal(*lat2_dms)
    lon2 = dms_to_decimal(*lon2_dms)

    # Konversi derajat ke radian
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lambda_rad = math.radians(lon2 - lon1)

    # Hitung arah Kiblat
    x = math.sin(delta_lambda_rad)
    y = math.cos(lat1_rad) * math.tan(lat2_rad) - math.sin(lat1_rad) * math.cos(delta_lambda_rad)
    qibla_direction_rad = math.atan2(x, y)

    # Konversi arah Qibla dari radian ke derajat
    qibla_direction_deg = math.degrees(qibla_direction_rad)

    # Sesuaikan arah Qibla agar berada dalam rentang [0, 360)
    qibla_direction_deg_adjusted = qibla_direction_deg
    if qibla_direction_deg_adjusted < 0:
        qibla_direction_deg_adjusted += 360

    return lat1, lon1, lat2, lon2, lat1_rad, lat2_rad, delta_lambda_rad, x, y, qibla_direction_rad, qibla_direction_deg, qibla_direction_deg_adjusted

# Fungsi untuk menghitung jarak menggunakan metode Vincenty
def vincenty_distance(lat1, lon1, lat2, lon2):
    a = 6378137.0  # Semi-major axis
    f = 1 / 298.257223563  # Flattening
    b = (1 - f) * a

    L = math.radians(lon2 - lon1)
    U1 = math.atan((1 - f) * math.tan(math.radians(lat1)))
    U2 = math.atan((1 - f) * math.tan(math.radians(lat2)))
    sinU1 = math.sin(U1)
    cosU1 = math.cos(U1)
    sinU2 = math.sin(U2)
    cosU2 = math.cos(U2)

    lambda_ = L
    lambda_prev = 0
    iter_limit = 1000

    while abs(lambda_ - lambda_prev) > 1e-12 and iter_limit > 0:
        sin_lambda = math.sin(lambda_)
        cos_lambda = math.cos(lambda_)
        sin_sigma = math.sqrt((cosU2 * sin_lambda) ** 2 +
                              (cosU1 * sinU2 - sinU1 * cosU2 * cos_lambda) ** 2)
        cos_sigma = sinU1 * sinU2 + cosU1 * cosU2 * cos_lambda
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cosU1 * cosU2 * sin_lambda / sin_sigma
        cos2_alpha = 1 - sin_alpha ** 2
        cos2_sigma_m = cos_sigma - 2 * sinU1 * sinU2 / cos2_alpha
        C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
        lambda_prev = lambda_
        lambda_ = L + (1 - C) * f * sin_alpha * (
                sigma + C * sin_sigma * (cos2_sigma_m + C * cos_sigma * (-1 + 2 * cos2_sigma_m ** 2))
        )
        iter_limit -= 1

    u2 = cos2_alpha * (a ** 2 - b ** 2) / (b ** 2)
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
    delta_sigma = B * sin_sigma * (
            cos2_sigma_m + B / 4 * (
            cos_sigma * (-1 + 2 * cos2_sigma_m ** 2) -
            B / 6 * cos2_sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos2_sigma_m ** 2)
    ))

    s = b * A * (sigma - delta_sigma)

    return s  # Jarak dalam meter

# Definisikan Query
@strawberry.type
class Query:
    @strawberry.field
    def calculate_solar(
        self, 
        latitude: str, 
        longitude: str, 
        datetime_str: str = None
    ) -> str:
        try:
            # Jika datetime_str tidak diberikan, gunakan waktu saat ini
            if datetime_str is None:
                datetime_str = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            
            # Parse latitude and longitude strings
            lat1_dms = latitude.split()
            lon1_dms = longitude.split()
            lat1_dms = (int(lat1_dms[0][:-1]), int(lat1_dms[1][:-1]), float(lat1_dms[2][:-1]), lat1_dms[3])
            lon1_dms = (int(lon1_dms[0][:-1]), int(lon1_dms[1][:-1]), float(lon1_dms[2][:-1]), lon1_dms[3])
            
            # Hitung arah Kiblat dan dapatkan nilai intermediate
            lat1, lon1, lat2, lon2, phi1, phi2, deltaLambda, x, y, qiblaDirectionRad, qiblaDirectionDeg, qiblaDirectionDegAdjusted = calculate_qibla_direction(lat1_dms, lon1_dms)

            # Hitung jarak antara lokasi pengamatan dan Ka'bah
            distance_meters = vincenty_distance(lat1, lon1, lat2, lon2)

            # Konversi jarak ke kilometer
            distance_km = distance_meters / 1000

            # Konversi koordinat pengamatan dan Ka'bah ke DMS
            lat1_dms_converted = to_dms(lat1)
            lon1_dms_converted = to_dms(lon1)

            lat2_dms_converted = to_dms(lat2)
            lon2_dms_converted = to_dms(lon2)

            # Format hasil ke dalam string
            output = f"""
1. Koordinat Lokasi Pengamatan:
    - Lintang (DMS): {lat1_dms_converted[0]}° {lat1_dms_converted[1]}’ {lat1_dms_converted[2]:.2f}” {'Selatan' if lat1 < 0 else 'Utara'}
    - Bujur (DMS): {lon1_dms_converted[0]}° {lon1_dms_converted[1]}’ {lon1_dms_converted[2]:.2f}” {'Barat' if lon1 < 0 else 'Timur'}

2. Konversi ke Derajat Desimal:
    - Lintang (ϕ₁): {lat1:.10f}°
    - Bujur (λ₁): {lon1:.10f}°

3. Koordinat Ka'bah:
    - Lintang (DMS): {lat2_dms_converted[0]}° {lat2_dms_converted[1]}’ {lat2_dms_converted[2]:.2f}” Utara
    - Bujur (DMS): {lon2_dms_converted[0]}° {lon2_dms_converted[1]}’ {lon2_dms_converted[2]:.2f}” Timur

4. Konversi ke Derajat Desimal:
    - Lintang (ϕ₂): {lat2:.10f}°
    - Bujur (λ₂): {lon2:.10f}°

5. Konversi ke Radian:
    - ϕ₁ = {lat1:.10f}° × π/180 = {phi1:.10f} rad
    - ϕ₂ = {lat2:.10f}° × π/180 = {phi2:.10f} rad
    - Δλ = ({lon2:.10f}° - {lon1:.10f}°) × π/180 = {deltaLambda:.10f} rad

6. Perhitungan Arah Kiblat:
    - sin(Δλ) = sin({deltaLambda:.10f}) = {math.sin(deltaLambda):.10f}
    - cos(ϕ₂) = cos({phi2:.10f}) = {math.cos(phi2):.10f}
    - x = sin(Δλ) = {math.sin(deltaLambda):.10f}
    - y = cos(ϕ₁) × tan(ϕ₂) - sin(ϕ₁) × cos(Δλ)
        = {math.cos(phi1):.10f} × {math.tan(phi2):.10f} - {math.sin(phi1):.10f} × {math.cos(deltaLambda):.10f}
        = {y:.10f}

7. Arah Kiblat (radian):
    - Q = atan2(x, y) = atan2({x:.10f}, {y:.10f}) = {qiblaDirectionRad:.10f} rad

8. Konversi ke Derajat:
    - Q = {qiblaDirectionRad:.10f} rad × 180/π = {qiblaDirectionDeg:.10f}°

9. Penyesuaian Arah Kiblat:
    Jika hasil awal perhitungan arah Kiblat (Q) kurang dari 0°, 
    itu menunjukkan bahwa arah tersebut berada di sisi kiri dari 0° (Utara) dalam sistem kompas. 
    Untuk mengubah arah ini menjadi positif dan sesuai dengan rentang [0, 360)°, 
    kita menambahkan 360°.
        - Sebelum penyesuaian: {qiblaDirectionDeg:.10f}°
        - Setelah penyesuaian: {qiblaDirectionDegAdjusted:.10f}°

10. Jarak antara lokasi pengamatan dan Ka'bah (Masjid al-Haram): {distance_km:.2f} kilometer

Kesimpulan:
    Arah Kiblat dari lokasi pengamatan {lat1_dms_converted[0]}° {lat1_dms_converted[1]}’ {lat1_dms_converted[2]:.2f}” {'Lintang Selatan' if lat1 < 0 else 'Lintang Utara'}, {lon1_dms_converted[0]}° {lon1_dms_converted[1]}’ {lon1_dms_converted[2]:.2f}” {'Bujur Barat' if lon1 < 0 else 'Bujur Timur'}
    menuju Ka'bah (Masjid al-Haram) adalah sebesar {qiblaDirectionDegAdjusted:.2f}° dari Utara.
    Jarak antara lokasi pengamatan dan Ka'bah adalah sekitar {distance_km:.2f} kilometer.
"""

            return output.strip()

        except Exception as e:
            return f"Error: {str(e)}"

# Buat skema
schema = strawberry.Schema(query=Query)

# Inisialisasi Flask
app = Flask(__name__)
app.add_url_rule("/graphql", view_func=GraphQLView.as_view("graphql_view", schema=schema))

if __name__ == "__main__":
    app.run(debug=True)
