from datetime import datetime
import hashlib

def registration_token(username, useremail):
	username = username
	useremail = useremail
	token = (username+useremail).encode('utf-8')

	return hashlib.md5(token).hexdigest()

def password_reset_token(username, useremail, userid):
	username = username
	useremail = useremail
	userid = str(userid)
	token = (username+useremail+userid).encode('utf-8')

	return hashlib.md5(token).hexdigest()
