from flask import Flask, render_template, request, url_for
import webview
import sys
import threading
import sqlite3
from datetime import datetime
from hashlib import sha256

app = Flask(__name__)

def adatbazis():
    global conn, cursor
    conn = sqlite3.connect('rapi.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `jegyek` (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, nev TEXT, email TEXT NOT NULL, kuldes BOOLEAN,  datum TIMESTAMP NOT NULL)")

@app.route('/')
def index():
    adatbazis()
    conn = sqlite3.connect("rapi.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("select * from jegyek")
    rows = cursor.fetchall();
    return render_template("index.html", rows=rows)
    
@app.route('/uj_jegy')
def uj_jegy():
    conn = sqlite3.connect("rapi.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("select max(id) from jegyek")
    rows = cursor.fetchall();
    for data in rows:
        max_id = data[0]
        current_id = int(max_id + 1)
        new_qrcode = sha256(str(current_id).encode('utf-8')).hexdigest()
    return render_template('uj_jegy.html', new_qrcode = new_qrcode)

@app.route('/post_jegy', methods = ['POST'])
def post_jegy():
    if request.method == 'POST':
        try:
            uj_nev = request.form['uj_nev']
            uj_email = request.form['uj_email']
            uj_datum = datetime.now()
            uj_kuldes = False
            with sqlite3.connect("rapi.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO jegyek (nev,email,kuldes,datum)
                VALUES(?,?,?,?)""",(uj_nev,uj_email,uj_kuldes,uj_datum) )
                conn.commit()
                msg = "Hozzaadva"
        except:
            conn.rollback()
            msg = "Error - Van baj"
        finally:
            #return index(msg=msg) # ehhez majd kell def index(msg) -> return ... msg=msg
            return index()
            conn.close()

def start_server():
    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':

    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    webview.create_window("RapiTickets", "http://localhost/", min_size=(1250, 650))
    webview.start()
    sys.exit()
