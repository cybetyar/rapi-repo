from datetime import datetime
import fitz
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def generate_and_send(qr_code,nev,email):
    today = datetime.today()

    document = fitz.open("d:\\python\\Rapi_pdf\\teszt.pdf")
    page = document[0]
    outfile = nev+".pdf"

                    #   X , Y
    p_name = fitz.Point(50, 72)  
    name = nev
    page.insert_text(p_name,name,fontname = "helv", fontsize = 30,rotate = 0 )

    p_date = fitz.Point(200, 150)
    date = today.strftime('%F')
    page.insert_text(p_date,date,fontname = "helv", fontsize = 30,rotate = 0 )


#                         x0, y0, x1, y1
    img_rect = fitz.Rect(0,100,200,200)
    page.insertImage(img_rect, filename="d:\\python\\Rapi_pdf\\qr_code.png", keep_proportion=True,align=1)

    document.save(outfile)
    document.close()


    smtp_server = "smtp.gmail.com"
    port = 587  
    sender_email = "bulykristof@gmail.com"
    password = "****"
    receiver_email = email

    body = "Üdv Rapis!"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Rapifeszt jegy"
    #message.attach(MIMEText(body, "plain"))

    with open('index.html', 'r') as f:
        html_string = f.read()
    


    with open(outfile, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)

    part.add_header("Content-Disposition",f"attachment; filename= {outfile}")

    message.attach(MIMEText(html_string, "html"))
    message.attach(part)


    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_email, password) #login with mail_id and password
    session.sendmail(sender_email, email, message.as_string())
    session.quit()


generate_and_send("d:\\python\\Rapi_pdf\\qr_code.png","Kristof","bulykristof@gmail.com")