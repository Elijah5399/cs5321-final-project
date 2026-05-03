from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
import base64
import time
import os
import json

app = Flask(__name__)

private_key_file = "private_key.pem"
public_key_file = "public_key.pem"

# load key if exist
if os.path.exists(private_key_file):
    with open(private_key_file, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
                key_file.read(),
                password=None)

else:
    private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )

    pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            )

    with open(private_key_file, "wb") as priv_key_file:
        priv_key_file.write(pem)

    print(f"pivate key generated, saved in {private_key_file}")

    public_key = private_key.public_key()

    pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

    with open(public_key_file, "wb") as pub_key_file:
        pub_key_file.write(pem)


public_key = private_key.public_key()

db_file = "signatures.json"

if os.path.exists(db_file):
    with open(db_file, "r") as file:
        db = json.load(file)

else:
    db= {}


def save_db():
    with open(db_file, "w") as file:
        json.dump(db, file, indent=4)

def create_signature(mac, ip, expiry):
    msg = f"{expiry}|{mac}|{ip}".encode()

    signature=private_key.sign(
            msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
                ),
            hashes.SHA256()

            )

    msg = msg.decode()
    signature = base64.b64encode(signature).decode()

    return msg, signature

def verify_signature(record):
    try:
        msg = f"{record['expiry']}|{record['mac']}|{record['ip']}".encode()
        signature = base64.b64decode(record['signature'])

        public_key.verify(
                signature,
                msg,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                    ),
                hashes.SHA256()
                )

        return True
    except Exception as error:
        print(f"error occured when verifying signature {error}")

        return False

@app.route("/verify", methods=["POST"])
def verify():

    data = request.json

    ip = data.get("ip")
    mac = data.get("mac")
    expiry = data.get("expiry")

    if not ip or not mac or not expiry:
        return jsonify({"error":"missing fields"}), 400


    to_delete = []
    for key, value in db.items():
        if value["ip"] == ip or value ["mac"] == mac:
            to_delete.append(key)

    for key in to_delete:
        del db[key]

    msg, signature = create_signature(mac, ip, expiry)

    db[ip] = {
        "mac": mac,
        "ip" : ip,
        "expiry": expiry,
        "signature" : signature

            }

    save_db()

    return jsonify({
        "status":"stored",
        "message":msg,
        "signature":signature
        })


# checking purpose
@app.route("/check", methods=["POST"])
def check():
    data = request.json

    ip = data.get("ip")
    mac=data.get("mac")


    # check if any mising field
    if not ip or not mac:
        return jsonify({"status":"reject", "reason": "missing fields"}), 400

    record = db.get(ip)

    # we will reject if it doesn't exist in our saved db
    if not record:
        return jsonify({"status":"reject", "reason": "no record"})

    # if invalid signature
    if not verify_signature(record):
        return jsonify({"status":"reject", "reason": "invalid signature"})

    # check expiry
    current_time = int(time.time())
    if current_time > int(record["expiry"]):
        return jsonify({"status":"reject", "reason": "expired"})

    # check mac match. if it doesnt match means arp poisoning occuring
    if mac != record["mac"]:
        return jsonify({"status":"reject", "reason": "mac mismatch"})

    return jsonify({"status": "accept"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
