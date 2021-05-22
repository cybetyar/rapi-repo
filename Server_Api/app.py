from flask import Flask, render_template, url_for, redirect, request, jsonify
import flask_login
import json

app = Flask(__name__)

app.secret_key = 'C947E1DC35A3F6BBEB6ADC1F5ACB4'

login_manager = flask_login.LoginManager()

login_manager.login_view = 'login'

login_manager.init_app(app)

users = {
'admin': {'password': 'R4P1F35ZT21!'}
}


class User(flask_login.UserMixin):
  pass


@login_manager.user_loader
def user_loader(email):
  if email not in users:
    return
  user = User()
  user.id = email
  return user


@login_manager.request_loader
def request_loader(request):
  email = request.form.get('email')
  if email not in users:
    return
  user = User()
  user.id = email
  user.is_authenticated = request.form['password'] == users[email]['password']
  return user


@app.route('/')
def index():
  return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
  if request.method == 'GET':
    return render_template("login.html")
  email = request.form['email']
  if request.form['password'] == users[email]['password']:
    user = User()
    user.id = email
    flask_login.login_user(user)
    return redirect(url_for('main'))
  return 'Helytelen felhasználónév vagy jelszó!'

@app.route('/value', methods=['GET','POST'])
def value():
    if request.method == 'POST':
        json_data = request.json
        qr_value = request.json['value']
        with open('logged.rapi') as file:
            contents = file.read()
            if qr_value in contents:
                return jsonify(status="A jegyet már felhasználták")
            else:
                with open('logged.rapi', 'a') as out:
                    out.write(qr_value + '\n')
                    out.close()
                return jsonify(status="Beléptetve")
    elif request.method == 'GET':
        with open('logged.rapi', 'r') as used_qr_file:
            used_qr_list = list()
            for used_qr in used_qr_file:
                used_qr.strip()
                used_qr_list.append({"qr": used_qr.strip()})
            get_response = jsonify(used_qr_list)
            get_response.headers.add('Access-Control-Allow-Origin', '*')
            return get_response
    else:
        return jsonify(status="Ez egy API")

@app.route('/main')
@flask_login.login_required
def main():
  return render_template('index.html')

if __name__ == "__main__":
  app.run(host="127.0.0.1",port=3000, ssl_context='adhoc')
