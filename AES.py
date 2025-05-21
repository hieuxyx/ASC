from flask import Flask, request, render_template_string, send_file, redirect, url_for
from Crypto.Cipher import AES
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Padding helper functions
def pad(data):
    return data + b"\0" * (AES.block_size - len(data) % AES.block_size)

def unpad(data):
    return data.rstrip(b"\0")

# AES encryption
def encrypt_file(file_path, key):
    key = key.ljust(32)[:32].encode()
    cipher = AES.new(key, AES.MODE_ECB)
    with open(file_path, 'rb') as f:
        data = pad(f.read())
    encrypted = cipher.encrypt(data)
    encrypted_path = file_path + '.enc'
    with open(encrypted_path, 'wb') as f:
        f.write(encrypted)
    return encrypted_path

# AES decryption
def decrypt_file(file_path, key):
    key = key.ljust(32)[:32].encode()
    cipher = AES.new(key, AES.MODE_ECB)
    with open(file_path, 'rb') as f:
        encrypted = f.read()
    decrypted = unpad(cipher.decrypt(encrypted))
    decrypted_path = file_path.replace('.enc', '.dec')
    with open(decrypted_path, 'wb') as f:
        f.write(decrypted)
    return decrypted_path

# Homepage HTML
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Chọn chức năng</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #74ebd5, #9face6);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            text-align: center;
        }
        h1 {
            margin-bottom: 30px;
            color: #333;
        }
        a.button {
            display: inline-block;
            padding: 12px 24px;
            margin: 10px;
            background-color: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 8px;
            transition: background-color 0.3s;
        }
        a.button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Chọn chức năng</h1>
        <a href="/encrypt" class="button">Mã hóa</a>
        <a href="/decrypt" class="button">Giải mã</a>
    </div>
</body>
</html>
'''

# Encrypt/Decrypt form template
FORM_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #74ebd5, #9face6);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .container {
            background-color: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            text-align: center;
            width: 400px;
            position: relative;
        }
        h1 {
            margin-bottom: 30px;
            color: #333;
        }
        input[type="text"], input[type="file"] {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ccc;
            border-radius: 8px;
            box-sizing: border-box;
        }
        input[type="submit"] {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            margin: 10px 5px;
            border-radius: 8px;
            cursor: pointer;
            transition: background-color 0.3s;
        }
        input[type="submit"]:hover {
            background-color: #45a049;
        }
        .back-button {
            position: fixed;
            top: 10px;
            left: 10px;
            background-color: red;
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            text-decoration: none;
            font-weight: bold;
        }
        .back-button:hover {
            background-color: darkred;
        }
    </style>
</head>
<body>
    <a href="/" class="back-button">&#8592; Quay lại</a>
    <div class="container">
        <h1>{{ title }}</h1>
        <form method="POST" enctype="multipart/form-data">
            <input type="text" name="key" placeholder="Nhập khóa (độ dài bất kỳ)" required><br>
            <input type="file" name="file" required><br>
            <input type="submit" value="{{ button }}">
        </form>
    </div>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        key = request.form['key']
        if uploaded_file and key:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)
            output_path = encrypt_file(file_path, key)
            return send_file(os.path.abspath(output_path), as_attachment=True)
    return render_template_string(FORM_TEMPLATE, title='Mã hóa', button='Mã hóa')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    if request.method == 'POST':
        uploaded_file = request.files['file']
        key = request.form['key']
        if uploaded_file and key:
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            uploaded_file.save(file_path)
            output_path = decrypt_file(file_path, key)
            return send_file(os.path.abspath(output_path), as_attachment=True)
    return render_template_string(FORM_TEMPLATE, title='Giải mã', button='Giải mã')

if __name__ == '__main__':
    app.run(debug=True)