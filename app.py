from flask import Flask, render_template, request, url_for
import webview
import sys
import threading
import sqlite3
from datetime import datetime

app = Flask(__name__)

def adatbazis():
    global conn, cursor
    conn = sqlite3.connect('rapi.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `jegyek` (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, nev TEXT, email TEXT NOT NULL, kuldes BOOLEAN,  datum TIMESTAMP NOT NULL)")

@app.route('/')
def index():
    adatbazis()
    con = sqlite3.connect("rapi.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from jegyek")
    rows = cur.fetchall();
    return render_template("index.html", rows=rows)
    
@app.route('/uj_jegy')
def uj_jegy():
    con = sqlite3.connect("rapi.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select max(id) from jegyek")
    rows = cur.fetchall();
    for data in rows:
        max_id = data[0]
    return render_template('uj_jegy.html', max_id = max_id)

@app.route('/post_jegy', methods = ['POST'])
def post_jegy():
    if request.method == 'POST':
        try:
            uj_nev = request.form['uj_nev']
            uj_email = request.form['uj_email']
            uj_datum = datetime.now()
            uj_kuldes = False
            with sqlite3.connect("rapi.db") as con:
                cur = con.cursor()
                cur.execute("""INSERT INTO jegyek (nev,email,kuldes,datum)
                VALUES(?,?,?,?)""",(uj_nev,uj_email,uj_kuldes,uj_datum) )
                con.commit()
                msg = "Hozzaadva"
        except:
            con.rollback()
            msg = "Error - Van baj"
        finally:
            #return render_template("hozaaadva.html", msg=msg)
            return index(msg=msg)
            con.close()

def start_server():
    app.run(host='0.0.0.0', port=80)

if __name__ == '__main__':

    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    webview.create_window("RapiTickets", "http://localhost/", min_size=(1250, 650))
    webview.start()
    sys.exit()
