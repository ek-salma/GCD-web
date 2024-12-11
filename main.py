import math
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pyproj import Proj, Geod

# Inisialisasi Flask
app = Flask(__name__, static_folder='static')
CORS(app)  # Aktifkan CORS

# Inisialisasi proyeksi Azimuthal Equidistant
proj_aeqd = Proj(proj='aeqd', lat_0=0, lon_0=0, datum='WGS84')  # Titik pusat default di (0, 0)

# Fungsi menghitung jarak proyeksi menggunakan Azimuthal Equidistant
def projected_distance(lat1, lon1, lat2, lon2):
    x1, y1 = proj_aeqd(lon1, lat1)
    x2, y2 = proj_aeqd(lon2, lat2)
    distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return round(distance, 2)

# Fungsi menghitung azimuth menggunakan Geod
def projected_azimuth(lat1, lon1, lat2, lon2):
    geod = Geod(ellps="WGS84")  # Model ellipsoid
    azimuth, _, _ = geod.inv(lon1, lat1, lon2, lat2)
    return azimuth % 360  # Normalize to 0-360

# Endpoint untuk menghitung jarak dan azimuth berbasis proyeksi
@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form
        lat1 = float(data['lat1'])
        lon1 = float(data['lon1'])
        lat2 = float(data['lat2'])
        lon2 = float(data['lon2'])

        # Hitung jarak dan azimuth berbasis proyeksi
        distance_proj = projected_distance(lat1, lon1, lat2, lon2)
        azimuth_proj = projected_azimuth(lat1, lon1, lat2, lon2)

        return jsonify({
            'projected_distance': distance_proj,
            'projected_azimuth': azimuth_proj,
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 400

# Endpoint untuk menghidangkan file HTML
@app.route('/')
def index():
    return app.send_static_file('index.html')

# Menjalankan aplikasi
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)