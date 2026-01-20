from scapy.all import rdpcap
from scapy.layers.inet import IP, TCP
import pandas as pd
#This Python script processes network traffic captures (PCAP) to extract to CVS

pcap_file = "part1-csv01.pcapng"
output_csv = "group01_http_input.csv"    

packets = rdpcap(pcap_file)

rows = []
msg_id = 1

HTTP_METHODS = ("GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH")

# Start time (first packet)
start_time = float(packets[0].time)

for pkt in packets:
    if not (pkt.haslayer(IP) and pkt.haslayer(TCP)):
        continue

    tcp = pkt[TCP]

    # HTTP = port 80
    if tcp.sport != 80 and tcp.dport != 80:
        continue

    if not pkt.haslayer("Raw"):
        continue

    try:
        payload = pkt["Raw"].load.decode(errors="ignore")
    except:
        continue

    first_line = payload.split("\r\n")[0]

    # HTTP request
    if first_line.startswith(HTTP_METHODS):
        message = first_line

    # HTTP response
    elif first_line.startswith("HTTP/"):
        message = first_line

    else:
        continue

    # Relative timestamp with 6 decimals
    timestamp = round(float(pkt.time) - start_time, 6)

    rows.append([
        msg_id,
        "HTTP",
        pkt[IP].src,
        pkt[IP].dst,
        message,
        f"{timestamp:.6f}"
    ])

    msg_id += 1

df = pd.DataFrame(rows, columns=[
    "msg_id",
    "app_protocol",
    "src_app",
    "dst_app",
    "message",
    "timestamp"
])

df.to_csv(output_csv, index=False)

print(f"Saved {len(df)} HTTP messages to {output_csv}")
