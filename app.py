from flask import Flask, render_template, request
import rsa, base64, os, json
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
HISTORY_FILE = 'history.json'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

(pubkey, privkey) = rsa.newkeys(2048)

def save_history(entry):
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    history.append(entry)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

@app.route('/', methods=['GET', 'POST'])
def index():
    msg = ''
    signature_b64 = ''
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            msg = 'Vui lòng chọn file để tải lên.'
        else:
            filedata = file.read()
            filename = file.filename

            # Ký file dữ liệu
            signature = rsa.sign(filedata, privkey, 'SHA-256')
            signature_b64 = base64.b64encode(signature).decode()

            # Lưu file vào thư mục uploads
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(save_path, 'wb') as f:
                f.write(filedata)

            # Lưu lịch sử
            save_history({
                "filename": filename,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "signature": signature_b64
            })
            msg = f"Đã ký và lưu file '{filename}'."

    history = load_history()
    return render_template('index.html', msg=msg, signature=signature_b64, history=history)

if __name__ == '__main__':
    app.run(debug=True)
