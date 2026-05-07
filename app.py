from flask import Flask, render_template, request, jsonify, redirect, url_for
import os

app = Flask(__name__)

# إعداد المجلدات لحفظ الصور
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# قاعدة بيانات مؤقتة (تصفر عند إغلاق البرنامج)
data = {
    "goal": 1000000,
    "current": 0,
    "all_donations": []
}

@app.route('/')
def index():
    percent = int((data['current'] / data['goal']) * 100) if data['goal'] > 0 else 0
    return render_template('index.html', stats=data, percent=percent)

@app.route('/upload', methods=['POST'])
def upload():
    amount = request.form.get('amount')
    file = request.files.get('receipt')
    if amount and file:
        filename = f"{len(data['all_donations'])}_{file.filename}"
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        data['all_donations'].insert(0, {
            "id": len(data['all_donations']),
            "amount": int(amount),
            "img": filename,
            "status": "⏳ قيد الانتظار"
        })
        return jsonify({"message": "تم الإرسال! سيظهر تبرعك في السجل كـ 'قيد الانتظار'."})
    return jsonify({"message": "خطأ في البيانات"}), 400

@app.route('/review_panel')
def review_panel():
    return render_template('admin_simple.html', donations=data['all_donations'])

@app.route('/action/<int:d_id>/<string:act>')
def action(d_id, act):
    for d in data['all_donations']:
        if d['id'] == d_id and "قيد الانتظار" in d['status']:
            if act == 'approve':
                d['status'] = "✅ تمت الموافقة"
                data['current'] += d['amount']
            else:
                d['status'] = "❌ مرفوض"
    return redirect(url_for('review_panel'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
