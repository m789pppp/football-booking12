import json
import gspread
from flask import Flask, request
from oauth2client.service_account import ServiceAccountCredentials
import requests
from base64 import b64decode
from io import BytesIO

# =======================
# إعداد Flask
# =======================
app = Flask(__name__)

# =======================
# إعداد Google Sheets
# =======================
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

SHEET_ID = "1BNNJwG3XIj5wY-m9hqVGGxEuUNLdYl3557XlzTqpnW8"  # ضع هنا الـ Sheet ID من الرابط
sheet = client.open_by_key(SHEET_ID).sheet1

# =======================
# Imgbb API Key
# =======================
IMGBB_API_KEY = "dfde267af77842f803122c8dab4c023a"

# =======================
# رفع صورة على Imgbb
# =======================
def upload_image(file_data):
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": IMGBB_API_KEY},
        files={"image": file_data}
    )
    if response.status_code == 200:
        return response.json()['data']['url']
    else:
        return ""

# =======================
# POST: إضافة حجز
# =======================
@app.route('/', methods=['POST'])
def add_booking():
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    field = data.get('field')
    time_slot = data.get('time')
    payment = data.get('payment')
    status = data.get('status')
    img_base64 = data.get('img_base64', None)

    # رفع الصورة إذا موجودة
    img_url = ""
    if img_base64:
        img_data = b64decode(img_base64.split(",")[1])
        img_url = upload_image(BytesIO(img_data))

    # التحقق من الحجز المكرر
    booked = sheet.get_all_records()
    for row in booked:
        if row['الملعب'] == field and row['الوقت'] == time_slot:
            return {"success": False, "message": "تم حجز هذا الملعب في هذا الوقت بالفعل"}, 400

    row = [name, phone, field, time_slot, payment, status, img_url]
    sheet.append_row(row)
    return {"success": True, "img_url": img_url}, 200

# =======================
# GET: استرجاع الحجوزات
# =======================
@app.route('/booked', methods=['GET'])
def get_booked_times():
    booked = sheet.get_all_records()
    return {"booked": booked}, 200

# =======================
# تشغيل السيرفر
# =======================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
