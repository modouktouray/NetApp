from flask import Flask, render_template, request
from netmiko import ConnectHandler
from twilio.rest import Client
from cryptography.fernet import Fernet

app = Flask(__name__)

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()

    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(data)

    with open(file_path, 'wb') as file:
        file.write(encrypted_data)

key = Fernet.generate_key()

encrypt_file('credentials.txt', key)

def decrypt_file(file_path, key):
    with open(file_path, 'rb') as file:
        data = file.read()

    fernet = Fernet(key)
    decrypted_data = fernet.decrypt(data)

    with open(file_path, 'wb') as file:
        file.write(decrypted_data)

decrypt_file('credentials.txt', key)

switch_credentials = {}

with open('credentials.txt', 'r') as file:
    for line in file:
        switch_name, ip, username, password = line.strip().split(',')
        switch_credentials[switch_name] = {
            'ip': ip,
            'username': username,
            'password': password
        }
# account_sid = ""
# auth_token = ""
# from_number = ""
# to_number = ""

# client = Client(account_sid, auth_token)
@app.route("/", methods=["POST"])
def get_port_statuses():
    selected_switch = request.form.get('switch')
    if selected_switch in switch_credentials:
        credentials = switch_credentials[selected_switch]
        switch = {
            'device_type': 'cisco_ios',
            'ip': credentials['ip'],
            'username': credentials['username'],
            'password': credentials['password']
        }
        try:
            net_connect = ConnectHandler(**switch)
            output = net_connect.send_command("show interface")
            statuses = {}
            port = ""
            for line in output.splitlines():
                # if line.startswith("Gi") and "notconnect" in line:
                #     message = client.messages.create(
                #         body="Port " + line.split()[0] + " is down on ",
                #         from_=from_number,
                #         to=to_number
                #     )
                #     print("Sent message:", message.sid)
                
                if "line protocol is" in line:
                    port = line.split()[0]
                    status = line.split()[-1]
                    statuses[port] = status
            switch_options = switch_credentials.keys()
            return render_template("index.html",switch_options=switch_options, statuses=statuses)
        except Exception as e:
            return f"Failed to connect to {selected_switch}: {str(e)}"
    else:
        return "Invalid switch selection."

def turn_on_port(port):
    
        # Send the command to turn on the port
    selected_switch = request.form.get('switch')
    if selected_switch in switch_credentials:
        credentials = switch_credentials[selected_switch]
        switch = {
            'device_type': 'cisco_ios',
            'ip': credentials['ip'],
            'username': credentials['username'],
            'password': credentials['password']
        }
        net_connect = ConnectHandler(**switch)
        conn.send_command(f"config t")
        conn.send_command(f"interface {port}")
        conn.send_command(f"no shutdown")

@app.route("/")
def index():
    switch_options = switch_credentials.keys()
    return render_template("index.html",switch_options=switch_options)

@app.route("/", methods=["POST"])
def input():
    port = request.form["port"]
    statuses = get_port_statuses()
    if statuses[port] == "notconnect":
        turn_on_port(port)
        return f"Port {port} was down and has been turned on"
    else:
        return f"Port {port} is already on"

if __name__ == "__main__":
    app.run()
