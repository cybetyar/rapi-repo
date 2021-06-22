from flask import Flask, render_template, request, url_for, jsonify
import webview
import sys
import threading
import sqlite3
from datetime import datetime
from hashlib import sha256
import fitz
import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import qrcode
from PIL import Image
import json
from currency_converter import CurrencyConverter

app = Flask(__name__)

def generate_and_send(uj_qr_value,uj_nev,uj_email):
    uj_nev = uj_nev.strip()
    today = datetime.today()

    document = fitz.open("static/pdf/template.pdf")
    page = document[0]
    outfile = "tickets/" + uj_nev + ".pdf"

    #   X , Y
    p_name = fitz.Point(625, 75)
    name = uj_nev
    page.insert_text(p_name, name, fontname="helv", fontsize=16, rotate=0)

    p_date = fitz.Point(625, 150)
    date = today.strftime('%F')
    page.insert_text(p_date, date, fontname="helv", fontsize=16, rotate=0)

    #generate image from uj_qr_value
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(uj_qr_value)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
    qr_img.save("tickets/current_qr.png")

    #                         x0, y0, x1, y1
    img_rect = fitz.Rect(255, 400, 355, 500)
    page.insertImage(img_rect, filename="tickets/current_qr.png", keep_proportion=True, align=1)

    document.save(outfile)
    document.close()

    #rapifeszt@protonmail.com/rapifeszt@gmail.com:Rz6ejLs87!z+vZ6
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "rapifeszt@gmail.com"
    password = "Rz6ejLs87!z+vZ6"
    receiver_email = uj_email

    #body = "Üdv Rapis!"
    message = MIMEMultipart('html')
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Rapifeszt jegy"
    # message.attach(MIMEText(body, "plain"))

    with open('static/pdf/email.html', 'r') as f:
        html_string = f.read()

    with open(outfile, "rb") as attachment:
        part = MIMEBase("application", "pdf",Name=outfile)
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header("Content-Disposition", f"attachment; filename= {outfile}")

    message.attach(MIMEText(html_string, "html"))
    message.attach(part)



    session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
    session.ehlo()
    session.starttls()  # enable security
    session.ehlo()
    session.login(sender_email, password)  # login with mail_id and password
    session.sendmail(sender_email, receiver_email, message.as_string())
    session.quit()
    os.remove("tickets/current_qr.png")

def adatbazis():
    global conn, cursor
    conn = sqlite3.connect('rapi.db')
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS `jegyek` (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, nev TEXT, email TEXT NOT NULL, statusz BOOLEAN, qr_kod TEXT, jegy_tipus INTEGER, datum TIMESTAMP NOT NULL)")


@app.route('/')
def index():
    adatbazis()
    #sysmsg = ''
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
        if max_id == None:
            max_id = 0
        current_id = int(max_id + 1)
        new_qrcode = sha256(str(current_id).encode('utf-8')).hexdigest()
    return render_template('uj_jegy.html', new_qrcode = new_qrcode)

@app.route('/show/<id>', methods=["GET"])
def show_qr(id):
    if request.method == 'GET':
        assert id == request.view_args['id']
        show_qr_value = sha256(str(id).encode('utf-8')).hexdigest()
        #generate image from uj_qr_value
        show_qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        show_qr.add_data(show_qr_value)
        show_qr.make(fit=True)
        show_qr_img = show_qr.make_image(fill_color="black", back_color="white").convert('RGB')
        show_qr_img.save("tickets/show_qr.png")
        show_im = Image.open('tickets/show_qr.png')
        show_im.show()
        os.remove("tickets/show_qr.png")
        return index()
#Mod
@app.route('/update/<id>', methods = ['POST'])
def update(id):
    if request.method == 'POST':
        assert id == request.view_args['id']
        req_data = request.json

        update_nev = req_data['update_nev']
        update_email = req_data['update_email']
        update_jegy_tipus = req_data['update_jegy_tipus']

        conn = sqlite3.connect("rapi.db")
        cur = conn.cursor()

        update_query = 'UPDATE jegyek SET nev = ?, email = ?, jegy_tipus = ? WHERE id = ?'
        cur.execute(update_query, (update_nev, update_email, update_jegy_tipus, id))
        conn.commit()

        conn.close()
        update_qrcode = sha256(str(id).encode('utf-8')).hexdigest()
        generate_and_send(update_qrcode, update_nev, update_email)
        #sysmsg = 'Módosítva'
        return jsonify(status = 'modositva')
#Mod vége

@app.route('/post_jegy', methods = ['POST'])
def post_jegy():
    if request.method == 'POST':
        try:
            uj_nev = request.form['uj_nev']
            uj_email = request.form['uj_email']
            uj_qr_value = request.form['qr_code_value']
            uj_datum = datetime.now()
            uj_statusz = False
            uj_jegy_tipus = request.form['uj_jegy_tipus']
            with sqlite3.connect("rapi.db") as conn:
                cursor = conn.cursor()
                cursor.execute("""INSERT INTO jegyek (nev,email,statusz,qr_kod,jegy_tipus,datum)
                VALUES(?,?,?,?,?,?)""",(uj_nev,uj_email,uj_statusz,uj_qr_value,uj_jegy_tipus,uj_datum) )
                conn.commit()
                #sysmsg = "Hozzaadva"
        except:
            conn.rollback()
            #sysmsg = "Error - Van baj"
        finally:
            #return index(msg=msg) # ehhez majd kell def index(msg) -> return ... msg=msg
            generate_and_send(uj_qr_value,uj_nev,uj_email)
            return index()
            conn.close()

@app.route('/osszesites', methods=["GET"])
def osszesites():
    if request.method == 'GET':
        conn = sqlite3.connect("rapi.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("select jegy_tipus from jegyek group by id")
        jegy_list = []
        rows = cursor.fetchall();
        for row in rows:
            jegy_list.append([x for x in row])
        flattened = [val for sublist in jegy_list for val in sublist]
        c = CurrencyConverter()
        current_eur = c.convert(1, 'EUR', 'HUF')
        if len(flattened) < 52:
            online = flattened.count(0)
            szemelyes = flattened.count(1)
            return jsonify(online_1=online,szemelyes_1=szemelyes,online_2="",szemelyes_2="",online_3="",szemelyes_3="",eur=current_eur)
        elif 52 < len(flattened) < 251:
            online_1 = flattened[:51].count(0)
            szemelyes_1 = flattened[:51].count(1)
            online_2 = flattened[51:].count(0)
            szemelyes_2 = flattened[51:].count(1)
            return jsonify(online_1=online_1, szemelyes_1=szemelyes_1, online_2=online_2, szemelyes_2=szemelyes_2, online_3="",
                           szemelyes_3="",eur=current_eur)
        else:
            online_1 = flattened[:51].count(0)
            szemelyes_1 = flattened[:51].count(1)
            online_2 = flattened[51::250].count(0)
            szemelyes_2 = flattened[51::250].count(1)
            online_3 = flattened[250:].count(0)
            szemelyes_3 = flattened[250:].count(1)
            return jsonify(online_1=online_1, szemelyes_1=szemelyes_1, online_2=online_2, szemelyes_2=szemelyes_2, online_3=online_3,
                           szemelyes_3=szemelyes_3,eur=current_eur)

def start_server():
    app.run(host='0.0.0.0', port=2491)

if __name__ == '__main__':

    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()

    webview.create_window("RapiTickets", "http://localhost:2491", min_size=(1250, 650))
    webview.start()
    sys.exit()
