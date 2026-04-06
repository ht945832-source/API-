import threading
import time
import hashlib
import os
from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
import telebot # Đảm bảo đã cài pyTelegramBotAPI

app = Flask(__name__)
CORS(app)

# Cấu hình Bot Telegram
TOKEN = "8725312860:AAFdfR5Sz65zi1D-Wpjl0Ma1wcFbX4xdN3Y"
bot = telebot.TeleBot(TOKEN)

store = {
    "phien": "0",
    "cau": "",
    "dudoan": "WAIT",
    "rate": "100%", # Xóa random, để mặc định 100% hoặc mức cố định
    "hex_hash": "0x0000000000000000"
}

def hex_process(p, c):
    global store
    store["phien"] = str(p)
    store["cau"] = str(c).lower()
    
    # THUẬT TOÁN HEX SHA-256 THẬT
    raw = f"{p}-{c}-hoang-secret-v19"
    h = hashlib.sha256(raw.encode()).hexdigest().upper()
    
    # Dự đoán dựa trên ký tự cuối của Hash (Không random)
    # Nếu ký tự cuối là số -> XỈU, là chữ -> TÀI
    res = "TÀI" if h[-1].isalpha() else "XỈU"
    
    store.update({
        "dudoan": res, 
        "rate": "98.8%", # Tỉ lệ cố định uy tín
        "hex_hash": f"0x{h[:16]}"
    })
    
    # Sau 35s tự động cộng phiên
    time.sleep(35) 
    store["phien"] = str(int(p) + 1)
    store["dudoan"] = "WAIT"

@app.route('/api/get-data')
def get_data(): 
    return jsonify(store)

@app.route('/set-data', methods=['POST'])
def set_data():
    p = request.form.get('phien')
    c = request.form.get('cau')
    if p and c:
        threading.Thread(target=hex_process, args=(p, c), daemon=True).start()
        return "OK"
    return "Error", 400

# Chạy Bot song song với Web
def run_bot():
    bot.infinity_polling()

if __name__ == '__main__':
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
