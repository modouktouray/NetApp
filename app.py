from flask import Flask, render_template, request
from netmiko import ConnectHandler

app = Flask(__name__)

# Define the credentials and IP address of the switch
device = {
    'device_type': 'cisco_ios',
    'ip': '10.217.4.5',
    'username': 'moici',
    'password': 'Moic1@GM'
}

# Define a function to get the status of all ports
def get_port_statuses():
    with ConnectHandler(**device) as conn:
        # Send the "show interface" command and get the output
        output = conn.send_command("show interface brief")
        # Parse the output to find the port statuses
        statuses = {}
        port = ""
        for line in output.splitlines():
            if "line protocol is" in line:
                port = line.split()[0]
                status = line.split()[-1]
                statuses[port] = status
        return statuses

# Define a function to turn on a port
def turn_on_port(port):
    with ConnectHandler(**device) as conn:
        # Send the command to turn on the port
        conn.send_command(f"config t")
        conn.send_command(f"interface {port}")
        conn.send_command(f"no shutdown")

# Define a route to display the port statuses and input form
@app.route("/")
def index():
    # Get the port statuses
    statuses = get_port_statuses()
    # Render the template with the statuses
    return render_template("index.html", statuses=statuses)

# Define a route to handle the input form
@app.route("/", methods=["POST"])
def input():
    # Get the port number from the form input
    port = request.form["port"]
    # Turn on the port if it is down
    statuses = get_port_statuses()
    if statuses[port] == "down":
        turn_on_port(port)
        return f"Port {port} was down and has been turned on"
    else:
        return f"Port {port} is already on"

if __name__ == "__main__":
    app.run()
