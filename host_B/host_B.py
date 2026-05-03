from flask import Flask, request, jsonify
import socket
import subprocess


app = Flask(__name__)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        my_ip = s.getsockname()[0]
    finally:
        s.close()
    return my_ip


def get_mac():
    try:
        mac = open('/sys/class/net/enp0s3/address').readline().strip()
    except Exception as error:
        print(f"Error as occured {error}")
        mac = "00:00:00:00:00:00"

    return mac



@app.route("/arp_reply", methods=["POST"])
def arp_reply():
    data = request.json
    requested_ip = data.get("ip")

    my_ip = get_ip()
    my_mac = get_mac()

    print(f"my ip: {my_ip}")
    print(f"my mac: {my_mac}")
    print(f"requested ip {requested_ip}")

    if requested_ip == my_ip:
        return jsonify({
            "ip":my_ip,
            "mac":my_mac
            })

    else:
        return jsonify({"status": "ignore"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
