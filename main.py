import math
import os  # Tambahkan untuk membaca environment variable
from flask import Flask, request, jsonify
from flask_cors import CORS  # Tambahkan CORS

app = Flask(__name__, static_folder='static')  # Tambahkan static_folder
CORS(app)  # Aktifkan CORS untuk menerima request dari HTML

# Fungsi menghitung jarak Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius Bumi dalam kilometer
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)

# Fungsi menghitung azimuth awal
def calculate_azimuth(lat1, lon1, lat2, lon2):
    d_lon = math.radians(lon2 - lon1)
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)

    x = math.sin(d_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(d_lon))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360  # Normalize to 0-360 degrees
    return compass_bearing

# Fungsi interpolasi jalur Great Circle
def interpolate_points(lat1, lon1, lat2, lon2, num_points=100):
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    delta_lon = lon2 - lon1
    a = math.cos(lat2) * math.sin(delta_lon)
    b = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    delta_sigma = math.atan2(math.sqrt(a**2 + b**2), math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(delta_lon))
    
    points = []
    for fraction in [i / num_points for i in range(num_points + 1)]:
        A = math.sin((1 - fraction) * delta_sigma) / math.sin(delta_sigma)
        B = math.sin(fraction * delta_sigma) / math.sin(delta_sigma)
        x = A * math.cos(lat1) * math.cos(lon1) + B * math.cos(lat2) * math.cos(lon2)
        y = A * math.cos(lat1) * math.sin(lon1) + B * math.cos(lat2) * math.sin(lon2)
        z = A * math.sin(lat1) + B * math.sin(lat2)
        lat = math.atan2(z, math.sqrt(x**2 + y**2))
        lon = math.atan2(y, x)
        points.append((math.degrees(lat), math.degrees(lon)))
    return points

# Endpoint untuk menghitung jarak dan interpolasi
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        lat1 = float(request.form['lat1'])
        lon1 = float(request.form['lon1'])
        lat2 = float(request.form['lat2'])
        lon2 = float(request.form['lon2'])

        print(f"Received: lat1={lat1}, lon1={lon1}, lat2={lat2}, lon2={lon2}")

        # Hitung jarak, azimuth, dan jalur interpolasi
        distance = haversine(lat1, lon1, lat2, lon2)
        azimuth = calculate_azimuth(lat1, lon1, lat2, lon2)
        points = interpolate_points(lat1, lon1, lat2, lon2)

        return jsonify({
            'distance': distance,
            'azimuth': azimuth,
            'points': [[point[0], point[1]] for point in points]
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 400

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Baca port dari environment variable
    app.run(host='0.0.0.0', port=port, debug=True)  # Pastikan host adalah 0.0.0.0
