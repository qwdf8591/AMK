from flask import Flask,url_for,request,redirect,render_template,session,send_from_directory 
from flask_login import LoginManager,UserMixin,login_user,current_user,login_required,logout_user
from flask_mail import Mail,Message
import json,os,time
import mysql.connector


app = Flask(__name__)

#flask-login
app.secret_key = 'your secret key'
login_manager = LoginManager(app)

#database
db=mysql.connector.connect(host = "127.0.0.1",user = "your sql account",password = "your sql password",database = "ST",auth_plugin='mysql_native_password')
cursor=db.cursor()

#flask-mail
app.config.update(
	MAIL_SERVER='smtp.live.com',
	MAIL_PROT=587,
	MAIL_USE_TLS=True,
	MAIL_USERNAME='your hotmail email',
	MAIL_PASSWORD='your password'
)
mail = Mail(app)

#rsa
conversion=['Q','A','Z','W','S','X','E','D','C','R','F','V','T','G','B','Y','H','N','U','J','M','I','K',',','O','L','.','P',';','!', \
'1','2','3','4','5','6','7','8','9','0','?','q','a','z','w','s','x','e','d','c','r','f','v','t','g','b','y','h','n','u','j','m','i', \
'k','o','l','p',' ']
def digitalize(p):
	decimal_string=[]
	for i in range(len(p)):
		decimal_string.append(conversion.index(p[i]))
	return decimal_string
def encrypt(plaintext,public_key):
	e=int(public_key[1:public_key.index(',')])
	n=int(public_key[public_key.index(',')+1:-1])
	decimal_string=digitalize(plaintext)
	cipher=[str(i**e%n) for i in decimal_string]
	return ",".join(cipher)
def decrypt(ciphertext,private_key):
	d=int(private_key[1:private_key.index(',')])
	n=int(private_key[private_key.index(',')+1:-1])
	ciphertext=ciphertext.split(',')
	plain=[conversion[(int(i)**d)%n] for i in ciphertext]
	return ''.join(plain)

class User(UserMixin):
	pass

def send_email(recipient,r_time):
	msg_title = 'Confirm to register Secret-Talk'
	msg_sender = 'youremail'
	msg_recipients = recipient
	msg_body = 'http://127.0.0.1:5000/confirm/'+str(r_time)
	msg = Message(msg_title,sender=('ST',msg_sender),recipients=msg_recipients)
	msg.body = msg_body
	mail.send(msg)

@login_manager.user_loader
def user_loader(account):

	command="SELECT * FROM usersign WHERE ACCOUNT='%s'" % account
	cursor.execute(command)
	result = cursor.fetchone()
	if result==None:
		return
	user = User()
	user.id = account
	return user

@app.route('/',methods=['GET','POST'])
def index():
	if current_user.is_authenticated:
		command="SELECT * FROM information WHERE ACCOUNT='%s'" % current_user.id
		cursor.execute(command)
		result = cursor.fetchone()
		return render_template('index.html',login=current_user.is_authenticated,username=result[1])
	else:
		return render_template('index.html',login=current_user.is_authenticated)

@app.route('/register/',methods=['GET','POST'])
def register():
	if request.method=='POST':
		command="SELECT * FROM information where account='%s'" % request.form['userid']
		cursor.execute(command)
		result = cursor.fetchone()
		if result==None:
			command="SELECT * FROM unconfirm WHERE ACCOUNT='%s'" % request.form['userid']
			cursor.execute(command)
			result = cursor.fetchone()
		if result != None:
			return render_template('register.html',alert='此帳號已有人註冊',nick=request.form['username'])
		elif request.form['userpw']!=request.form['conf_pw']:
			return render_template('register.html',alert='密碼與確認密碼不同',id=request.form['userid'],nick=request.form['username'])
		else:
			command = "INSERT INTO unconfirm VALUES (%s,%s,%s,%s,%s,%s)"
			register_time=time.time()
			val=(request.form['userid'],request.form['userpw'],request.form['username'],request.form['email'],request.form['public_key'],register_time)
			cursor.execute(command, val)
			db.commit()
			send_email([request.values['email']],register_time)
			return redirect(url_for('confirm')) 
		return redirect(url_for('index'))
	return render_template('register.html')

@app.route('/confirm/')
@app.route('/confirm/<rtime>')
def confirm(rtime=None):
	if rtime==None:
		return render_template('confirm.html',confirm="first")
	else:
		command="SELECT * FROM unconfirm WHERE register='%s'" % rtime
		cursor.execute(command)
		result = cursor.fetchone()
		if result == None:
			return render_template('confirm.html',confirm="timeout")
		else:
			command="INSERT INTO information VALUES (%s,%s,%s,%s)"
			val=(result[0],result[2],result[3],result[4])
			cursor.execute(command,val)
			command="INSERT INTO usersign VALUES (%s,%s)"
			val=(result[0],result[1])
			cursor.execute(command,val)
			command="DELETE FROM unconfirm WHERE register='%s'" % rtime
			cursor.execute(command)
			db.commit()

			return render_template('confirm.html',confirm="yes")

@app.route('/login/',methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	command="SELECT * FROM usersign WHERE ACCOUNT='%s'" % request.form['userid']
	cursor.execute(command)
	result = cursor.fetchone()

	if request.form['userpw'] == result[1]:
		user = User()
		user.id = request.form['userid']
		login_user(user)
		session['private_key']=''
		return redirect(url_for('index'))
	return render_template('login.html',alert='帳號密碼輸入錯誤')

@app.route('/download/')
def download():
	path=os.path.dirname(__file__)
	return send_from_directory(path, 'rsa.exe', as_attachment=True)

@app.route('/logout/')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/send/',methods=['GET','POST'])
def send():
	if request.method=='POST':
		command = "SELECT * FROM information WHERE ACCOUNT='%s'" % request.form['receiver']
		cursor.execute(command)
		result = cursor.fetchone()
		c_theme=encrypt(request.form['title'],result[3])
		c_content=encrypt(request.form['content'],result[3])
		command = "INSERT INTO mailbox(SENDER,RECEIVER,UNREAD,THEME,CONTENT) VALUES (%s,%s,%s,%s,%s)"
		val=(current_user.id,request.form['receiver'],True,c_theme,c_content)
		cursor.execute(command, val)
		db.commit()
		return redirect(url_for('index'))
	return render_template('send.html')

@app.route('/receive/',methods=['GET','POST'])
@app.route('/receive/<mailid>',methods=['GET','POST'])
def receive(mailid=None):

	if session['private_key']=='':
		if request.method=='GET':
			return render_template('private_key.html')
		else:
			session['private_key']=request.form['private_key']
	if mailid==None:
		if request.form.get('select')!=None:
			if request.form.get('select')=='全部信件':
				command="SELECT * FROM mailbox WHERE RECEIVER='%s'" % current_user.id
			elif request.form.get('select')=='未讀信件':
				command="SELECT * FROM mailbox WHERE RECEIVER='%s' AND UNREAD=1" % current_user.id
			elif request.form.get('select')=='已讀信件':
				command="SELECT * FROM mailbox WHERE RECEIVER='%s' AND UNREAD=0" % current_user.id
			elif request.form.get('select')=='好友信件':
				command="SELECT * FROM mailbox INNER join friend on (mailbox.RECEIVER=friend.ACCOUNT AND mailbox.SENDER=friend.FRIEND) WHERE RECEIVER='%s'" % current_user.id
			elif request.form.get('select')=='陌生信件':
				command="SELECT * FROM mailbox LEFT JOIN friend on (mailbox.RECEIVER=friend.ACCOUNT AND mailbox.SENDER=friend.FRIEND) WHERE ACCOUNT IS NULL AND RECEIVER='%s'" % current_user.id
			elif request.form.get('select')=='系統信件':
				command="SELECT * FROM mailbox WHERE RECEIVER='%s' AND SENDER='system'" % current_user.id
			cursor.execute(command)
			result = cursor.fetchall()
			new_result=[]
			for row in result:
				title=decrypt(row[4],session['private_key'])
				content=decrypt(row[5],session['private_key'])
				new_result.append([row[0],row[1],row[2],title,content])
			return render_template('receive.html',maildict=new_result)	

		else:
			command="SELECT * FROM mailbox WHERE RECEIVER='%s'" % current_user.id
			cursor.execute(command)
			result = cursor.fetchall()
			new_result=[]
			for row in result:
				title=decrypt(row[4],session['private_key'])
				content=decrypt(row[5],session['private_key'])
				new_result.append([row[0],row[1],row[2],title,content])
			return render_template('receive.html',maildict=new_result)
	else:
		command="SELECT * FROM mailbox WHERE MAILID='%s'" % mailid
		cursor.execute(command)
		result = cursor.fetchone()
		command="UPDATE mailbox SET UNREAD='%s' WHERE MAILID='%s'" % (0,mailid)
		cursor.execute(command)
		db.commit()
		title=decrypt(result[4],session['private_key'])
		content=decrypt(result[5],session['private_key'])
		return render_template('mail.html',mailinform=[result[0],result[1],result[2],title,content])


@app.route('/friend/',methods=['GET','POST'])
def friend():
	if request.method=='POST':
		command = "INSERT INTO friend VALUES (%s,%s)"
		val=(current_user.id,request.form['f_account'])
		cursor.execute(command, val)
		db.commit()
		if request.form.get('notify')=='yes':
			title="System mail"
			message=current_user.id+" request to be your friend."
			command = "SELECT * FROM information WHERE ACCOUNT='%s'" % request.form['f_account']
			cursor.execute(command)
			result = cursor.fetchone()
			c_theme=encrypt(title,result[3])
			c_content=encrypt(message,result[3])
			command = "INSERT INTO mailbox(SENDER,RECEIVER,UNREAD,THEME,CONTENT) VALUES (%s,%s,%s,%s,%s)"
			val=('System',request.form['f_account'],True,c_theme,c_content)
			cursor.execute(command, val)
			db.commit()
	return render_template('add_friend.html')


if __name__ == '__main__':
	app.run(debug=True)
