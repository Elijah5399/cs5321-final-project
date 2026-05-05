# cs5321-final-project
Code repository for CS5321 final project. A simplified simulation of ARP with authentication

# SignARP
This project is a demonstration for CS5321

---

## Network Setup
Each device is hosted individually on a virtual machine
- **DHCP Server**: 192.168.56.254
    - Running isc-dhcp-server
        - Range: 192.168.56.2 - 192.168.56.100
        - Netmask: 255.255.255.0
        - Router: 192.168.56.254
- **Verification Server**: 192.168.56.20
- **Host A**: IP Address given by DHCP Server
- **Host B**: 
    - Initially: 192.168.56.107 to show that Host A rejects
    - Later reassigned an IP Address by DHCP Server during demonstration to show that it is accepted

# Idea

## Phase 1 (DHCP)
1. Host A broadcasts a DHCP request for 192.168.56.<>
2. DHCP Server replies with DHCP Ack
3. DHCP Server sends the information to the verification server
4. Verification server will create a signature for the MAC - IP Address binding: signA = Sign(sk, expiry ||aa|| ip addr)
5. Verification server will store the signature A 

## Phase 2 (ARP)
1. Host A is asking for 192.168.56.107
2. Host B reply with "bb has 192.168.56.107" 
3. Host A will receive this information and send the information to verification server, and wait for verification server reply
4. Verification server will find the signature for B
5. Verification server will do a verification check, verify(sk, sigB)
6. Verification server will send accept if it's verified, else it will send reject to Host A
7. Host A will receive the packet from Verification server and update arp table accordingly


# Demonstration

## Phase 1 (DHCP Phase)

1. On DHCP Server, Verification server, Host B machine
2. On DHCP Server, remove the lease given by dhcp server
    - `sudo rm /var/lib/dhcp/dhcpd.leases`
3. On Verification server remove the initial signature.json (if exist)
    - `sudo rm ~/Desktop/signatures.json`
4. Start the script in the following order
    - Verification  server `“sudo ~/Desktop/veri_simulated.py”`
    - DHCP Server: `sudo systemctl start isc-dhcp-server`
    - DHCP Server: `sudo python3 ~/Desktop/dhcp_simulated.py`
5. On the Host A Machine
    - While Host A is on, it will request for DHCP from the DHCP Server, and you will see an update on the DHCP Server script & verification server script

## Phase 2 (ARP Phase)
To show that those that are not given by DHCP Server will be rejected
1. On Host B: `sudo python3 ~/Desktop/host_b.py`
2. On Host A: `sudo python3 ~/Desktop/phase_2_finalised.py`
    - It will ask for an ip address. Key in Host B current static IP Address: `192.168.56.107`
    - We will see that it is rejected
3. On Host B we change the network to DHCP & check for IP address assigned to it. 
4. On Host A: we key in the newly assigned ip address given to Host B, we we will see that it is accepted.


# Simulation link
If you would like to try the simulation yourself, you may download the OVA file below (Only available to people in NUS)
https://nusu-my.sharepoint.com/:u:/g/personal/e1122698_u_nus_edu/IQA0AeZ_yTTgSZwT3BiKUAXlAUTAL0rjh3KsYx88BupOCxs?e=owSZ5e