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

# switch_credentials = {}

# with open('credentials.txt', 'r') as file:
#     for line in file:
#         switch_name, ip, username, password = line.strip().split(',')
#         switch_credentials[switch_name] = {
#             'ip': ip,
#             'username': username,
#             'password': password
#         }
# account_sid = ""
# auth_token = ""
# from_number = ""
# to_number = ""

# client = Client(account_sid, auth_token)

def connect(device_type,ip,username,password,port):
        device = {
		'device_type': device_type,
		'ip': ip,
		'username': username,
		'password':  password,
		'port': port
		}
        return ConnectHandler(**device)    

@app.route("/", methods=["POST", "GET"])
def get_port_statuses():
    if request.method == 'POST':
        result = request.form.to_dict()
        device = connect('cisco_ios', result['hostname'], result['username'], result['password'] , result['port'])
        output = device.send_command("show interface")
        statuses = {}
        port = ""
        for line in output.splitlines():
            if "line protocol is" in line:
                port = line.split()[0]
                status = line.split()[-1]
                statuses[port] = status
        return render_template("index.html", statuses=statuses)
    else:
	    return render_template('index.html')

# def turn_on_port(port):
    
#         # Send the command to turn on the port
#     device = connect('cisco_ios', result['hostname'], result['username'], result['password'] , result['port'])
#     port = request.form["port"]
#     config_commands = ['interface ' + port, 'no shutdown']
#     output = net_connect.send_config_set(config_commands)

# @app.route("/")
# def index():
#     switch_options = switch_credentials.keys()
#     return render_template("index.html",switch_options=switch_options)

# @app.route("/", methods=["POST"])
# def input():
#     statuses = get_port_statuses()
#     if statuses[port] == "notconnect":
#         turn_on_port(port)
#         return f"Port {port} was down and has been turned on"
#     else:
#         return f"Port {port} is already on"

if __name__ == "__main__":
    app.run()
