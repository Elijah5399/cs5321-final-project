import requests
import subprocess

# fake arp table for demonstration
arp_table = {}

def request_arp(ip):
    print(f"Asking who has ip {ip}")

    # Connect to Host B to get MAC respond
    try:
        response = requests.post(host_b_url, json={"ip": ip}, timeout=3)
        data = response.json()
    except Exception as error:
        print(f"Error when requesting for MAC: {error}")
        return

    # Our response must include "mac" and "ip"
    print(data)
    if ("mac" not in data or "ip" not in data):
        print("Invalid response from Host B")
        return

    mac = data["mac"]
    ip = data["ip"]

    print(f"Arp Reply received: {mac} has {ip}")

    # VErification process from Verification server
    try:
        verify = requests.post(verify_url, json={
            "ip":ip,
            "mac":mac
            }, timeout=3)

        verify_data = verify.json()

    except Exception as error:
        print(f"Error when verifying {error}")
        return

    print(f"Verify data {verify_data}")
    # Accept if verification server replies with accept
    if (verify_data.get("status") == "accept"):
        print("Verified, ARP table will be updated")

        arp_table[ip] = mac

    else:
        print("Rejected. ARP table will not be updated")
        print(f"Reason is due to: {verify_data.get('reason')}")

    print(f"Current ARP table {arp_table}")

if __name__ == "__main__":
    while True:

        host_b_ip = input("What's the IP Address of Host B? ")
        verifying_server_ip = "192.168.56.20"

        host_b_url = f"http://{host_b_ip}:5001/arp_reply"
        verify_url = f"http://{verifying_server_ip}:5000/check"

        if host_b_ip.lower() == "exit":
            print("Good bye")
            break

        request_arp(host_b_ip)
