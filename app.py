from flask import Flask, render_template, request
from netmiko import ConnectHandler
from twilio.rest import Client
from cryptography.fernet import Fernet
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)


# def encrypt_file(file_path, key):
#     with open(file_path, 'rb') as file:
#         data = file.read()

#     fernet = Fernet(key)
#     encrypted_data = fernet.encrypt(data)

#     with open(file_path, 'wb') as file:
#         file.write(encrypted_data)

# key = Fernet.generate_key()

# encrypt_file('credentials.txt', key)

# def decrypt_file(file_path, key):
#     with open(file_path, 'rb') as file:
#         data = file.read()

#     fernet = Fernet(key)
#     decrypted_data = fernet.decrypt(data)

#     with open(file_path, 'wb') as file:
#         file.write(decrypted_data)

# decrypt_file('credentials.txt', key)

# account_sid = ""
# auth_token = ""
# from_number = ""
# to_number = ""

# client = Client(account_sid, auth_token)
@app.route("/")
def get_credentials():
    switch_credentials = []
    with open('credentials.txt', 'r') as f:
        for line in f:
            switch_info = line.strip().split(',')
            switch_ip = switch_info[1]
            switch_credentials.append(switch_ip)
    return render_template('index.html', switch_credentials=switch_credentials)
          
def connect(device_type,ip,username,password,port):
        device = {
		'device_type': device_type,
		'ip': ip,
		'username': username,
		'password':  password,
		'port': port
		}
        return ConnectHandler(**device)    
    
#Turning the port on
def turn_on_port():
    interface_name = request.form["port"]
    if interface_name:
        command = f'interface {interface_name}\nno shutdown\n'
        output = device.send_config_set(command)
        
#geting the ports info
@app.route("/switchinfo", methods=["POST", "GET"])
def get_port_statuses():
        if request.method == 'POST':
            #connecting to the device
            result = request.form.to_dict()
            device = connect('cisco_ios', result['ip'] , result['username'], result['password'] , result['port'])
            first_value = next(iter(result.values()))
            output = device.send_command("show interface")
            statuses = {}
            port = ""
            for line in output.splitlines():
                if "line protocol is" in line:
                    port = line.split()[0]
                    status = line.split()[-1]
                    statuses[port] = status
            return render_template("switch_info.html", statuses=statuses, first_value=first_value)
        else:
            return render_template('index.html')
 

if __name__ == "__main__":
    app.run()
