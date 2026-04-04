import time
import re
from datetime import datetime
import requests


lease_file = "/var/lib/dhcp/dhcpd.leases"
verify_host_url = "http://192.168.56.20:5000/verify"

seen = set()

def parse_lease():
    leases = []

    try:
        with open(lease_file, "r") as file:
            content = file.read()


        # find each block starting with <>.<>.<>.<>
        blocks = re.findall(r"lease (\d+\.\d+\.\d+\.\d+) {([^}]*)}", content)

        for ip, block in blocks:

            # find the mac addr
            mac_match = re.search(r"hardware ethernet ([0-9a-f:]+);", block)

            # get binding state
            binding_state = re.search(r"binding state (\w+);", block)

            if mac_match and binding_state:
                mac = mac_match.group(1)
                state = binding_state.group(1)

                if state== "active":
                    leases.append((ip, mac))

    except Exception as error:

        print(f"Error has ocured reading lease file {error}")

    return leases


def send_to_verification_server(ip, mac):
    # we give each lease 1 hr
    expiry = int(datetime.now().timestamp()) + 3600

    payload = {
            "ip" : ip,
            "mac": mac,
            "expiry": expiry
            }


    try:
        response = requests.post(verify_host_url, json=payload, timeout=5)
        print(f"sent to verification server to update database!")
        print(f"{ip} -> {mac}")
    except Exception as error:
        printf("Failed to send to verification server to update. Error: {error}")


if __name__ == "__main__":
    print("DHCP code started...")

    while True:
        leases = parse_lease()

        for ip, mac in leases:
            key = f"{ip}-{mac}"

            if key not in seen:
                send_to_verification_server(ip, mac)
                seen.add(key)

        time.sleep(5)