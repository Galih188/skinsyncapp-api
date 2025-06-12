import os
import io
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
from utils.recommend import get_recommendation
from datetime import datetime

# --------------------------------------------------------------------------
# Inisialisasi Aplikasi Flask dan Ekstensi
# --------------------------------------------------------------------------
app = Flask(__name__)

# Konfigurasi untuk ekstensi
app.config['JWT_SECRET_KEY'] = 'super-secret' # Ganti ini dengan kunci yang lebih aman
app.config['SECRET_KEY'] = 'another-super-secret'

# Mengaktifkan CORS untuk semua domain
CORS(app) 

# Inisialisasi ekstensi
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# --------------------------------------------------------------------------
# "Database" In-Memory untuk User
# --------------------------------------------------------------------------
users_db = {} 

# --------------------------------------------------------------------------
# Model & Fungsi Preprocessing Gambar
# --------------------------------------------------------------------------
model = load_model("model/model_jenis_kulit.h5")
skin_classes = ['dry', 'normal', 'oily']

def preprocess_image(img_bytes):
    """Fungsi untuk memproses gambar sebelum dimasukkan ke model."""
    img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0) / 255.0
    return img_array

# --------------------------------------------------------------------------
# Endpoint Sambutan (BARU)
# --------------------------------------------------------------------------
@app.route('/')
def home():
    """Endpoint root untuk mengecek status API."""
    return jsonify({
        "status": "online",
        "message": "Welcome to SkinSync API!",
        "timestamp": datetime.now().isoformat()
    }), 200

# --------------------------------------------------------------------------
# Endpoint untuk Otentikasi User
# --------------------------------------------------------------------------
@app.route('/auth/register', methods=['POST'])
def register():
    """Endpoint untuk registrasi user baru."""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'error': 'Data tidak lengkap'}), 400

    if email in users_db:
        return jsonify({'error': 'Email sudah terdaftar'}), 409

    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    users_db[email] = {'name': name, 'password_hash': password_hash}
    
    print("User terdaftar:", users_db)
    return jsonify({'message': 'Registrasi berhasil!'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    """Endpoint untuk login user."""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email atau password tidak boleh kosong'}), 400

    user = users_db.get(email)

    if user and bcrypt.check_password_hash(user['password_hash'], password):
        # Menggunakan email (sebuah string) sebagai identitas untuk token.
        access_token = create_access_token(identity=email)
        # Mensiapkan data user lengkap untuk dikirim ke frontend.
        user_data_for_frontend = {'name': user['name'], 'email': email}

        # Mengkirim token DAN data user.
        return jsonify(token=access_token, user=user_data_for_frontend)
        # -------------------------

    return jsonify({'error': 'Email atau password salah'}), 401

# --------------------------------------------------------------------------
# Endpoint untuk Fitur Utama (Analisis Kulit)
# --------------------------------------------------------------------------
@app.route('/predict', methods=['POST'])
@jwt_required() 
def predict():
    """Endpoint untuk memprediksi jenis kulit dari gambar."""
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file yang diunggah'}), 400

    file = request.files['file']
    
    try:
        img_bytes = file.read()
        img_array = preprocess_image(img_bytes)
        prediction = model.predict(img_array)
        
        class_idx = np.argmax(prediction)
        confidence = float(np.max(prediction)) * 100
        skin_type = skin_classes[class_idx]
        
        recommendation = get_recommendation(skin_type)
        
        descriptions = {
            "dry": "Kulit kering cenderung terasa kencang, terlihat kusam, dan terkadang mengelupas. Jenis kulit ini membutuhkan hidrasi ekstra.",
            "oily": "Kulit berminyak memproduksi sebum berlebih, membuatnya tampak berkilau dan rentan terhadap komedo serta jerawat.",
            "normal": "Kulit normal memiliki keseimbangan yang baik antara kelembapan dan minyak, serta jarang bermasalah."
        }
        description = descriptions.get(skin_type, "Deskripsi tidak tersedia.")

        return jsonify({
            'skin_type': skin_type,
            'confidence': f"{confidence:.2f}",
            'recommendations': recommendation,
            'description': description
        })
    except Exception as e:
        print(f"Error saat prediksi: {e}")
        return jsonify({'error': 'Gagal melakukan analisis. Pastikan file adalah gambar yang valid.'}), 500

# --------------------------------------------------------------------------
# Endpoint untuk Feedback
# --------------------------------------------------------------------------
@app.route('/feedback', methods=['POST'])
def feedback():
    """Endpoint untuk menerima feedback dari user."""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    if not name or not email or not message:
        return jsonify({'error': 'Semua field harus diisi'}), 400

    print("\n--- FEEDBACK DITERIMA ---")
    print(f"Nama: {name}")
    print(f"Email: {email}")
    print(f"Pesan: {message}")
    print("-------------------------\n")

    return jsonify({'message': 'Feedback Anda telah kami terima. Terima kasih!'}), 200

# --------------------------------------------------------------------------
# Menjalankan Aplikasi
# --------------------------------------------------------------------------
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)