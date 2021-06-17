import schedule
import time
import mysql.connector


db=mysql.connector.connect(host = "127.0.0.1",user = "root",password = "root",database = "ST",auth_plugin='mysql_native_password')
cursor=db.cursor()

def remove_unconfirm():
	command="SELECT * FROM unconfirm" 
	cursor.execute(command)
	result = cursor.fetchall()
	for row in result:
		if time.time()-float(row[5])>86400:
			command="DELETE FROM unconfirm WHERE account='%s'" % row[0]
			cursor.execute(command)
	db.commit()

schedule.every().day.at("00:00").do(remove_unconfirm)
while 1:
	schedule.run_pending()
