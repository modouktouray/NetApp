from flask import Flask, render_template, request
from netmiko import ConnectHandler
from twilio.rest import Client

app = Flask(__name__)

device = {
    'device_type': 'cisco_ios',
    'ip': '10.217.4.5',
    'username': 'moici',
    'password': 'Moic1@GM'
}

account_sid = "AC516de1b35de4f13bd5d3f1e65ec40785"
auth_token = "7200b102526e918c307faff56e69b8ea"
from_number = "+16076382857"
to_number = "+2203304726"

client = Client(account_sid, auth_token)


def get_port_statuses():
    with ConnectHandler(**device) as conn:
        output = conn.send_command("show interface")
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
        return statuses
    time.sleep(300)

def turn_on_port(port):
    with ConnectHandler(**device) as conn:
        # Send the command to turn on the port
        conn.send_command(f"config t")
        conn.send_command(f"interface {port}")
        conn.send_command(f"no shutdown")

@app.route("/")
def index():
    statuses = get_port_statuses()
    return render_template("index.html", statuses=statuses)

@app.route("/", methods=["POST"])
def input():
    port = request.form["port"]
    statuses = get_port_statuses()
    if statuses[port] == "down":
        turn_on_port(port)
        return f"Port {port} was down and has been turned on"
    else:
        return f"Port {port} is already on"

if __name__ == "__main__":
    app.run()
