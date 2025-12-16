import paramiko
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

# ========================
# CONFIGURAZIONE SSH PI
# ========================
PI_IP = "192.168.1.234"
PI_USER = "stefano"
PI_PASS = "1234"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(PI_IP, username=PI_USER, password=PI_PASS)

# ========================
# BUFFER DATI
# ========================
timestamps = []
cpu_perc = []
ram_perc = []
disk_perc = []
net_sent = []
net_recv = []
cpu_temp = []

# inizializzo net counters
stdin, stdout, stderr = ssh.exec_command("cat /proc/net/dev | grep eth0")
line = stdout.read().decode().strip()
if line:
    prev_recv = int(line.split()[1])
    prev_sent = int(line.split()[9])
else:
    prev_recv = 0
    prev_sent = 0

# ========================
# FUNZIONE PER OTTENERE STATISTICHE
# ========================
def get_stats():
    global prev_recv, prev_sent

    # --- CPU %
    try:
        stdin, stdout, stderr = ssh.exec_command("top -bn1 | grep 'Cpu(s)'")
        cpu_line = stdout.read().decode().strip()
        if cpu_line:
            parts = cpu_line.split(",")
            id_part = [p for p in parts if "%id" in p]
            idle = float(id_part[0].split("%")[0].strip()) if id_part else 0.0
            cpu_val = 100.0 - idle
        else:
            cpu_val = 0.0
    except:
        cpu_val = 0.0

    # --- RAM %
    try:
        stdin, stdout, stderr = ssh.exec_command("free | grep Mem")
        mem_line = stdout.read().decode().strip()
        if mem_line:
            total, used, *_ = [int(x) for x in mem_line.split()[1:4]]
            ram_val = used / total * 100
        else:
            ram_val = 0.0
    except:
        ram_val = 0.0

    # --- Disco %
    try:
        stdin, stdout, stderr = ssh.exec_command("df / | tail -1")
        disk_line = stdout.read().decode().strip()
        if disk_line:
            disk_val = float(disk_line.split()[4].replace("%",""))
        else:
            disk_val = 0.0
    except:
        disk_val = 0.0

    # --- Temperatura CPU
    try:
        stdin, stdout, stderr = ssh.exec_command("cat /sys/class/thermal/thermal_zone0/temp")
        temp_line = stdout.read().decode().strip()
        temp_val = float(temp_line)/1000.0 if temp_line else float('nan')
    except:
        temp_val = float('nan')

    # --- Rete (delta KB)
    try:
        stdin, stdout, stderr = ssh.exec_command("cat /proc/net/dev | grep eth0")
        line = stdout.read().decode().strip()
        if line:
            recv = int(line.split()[1])
            sent = int(line.split()[9])
            net_recv_val = (recv - prev_recv)/1024.0
            net_sent_val = (sent - prev_sent)/1024.0
            prev_recv, prev_sent = recv, sent
        else:
            net_recv_val = 0.0
            net_sent_val = 0.0
    except:
        net_recv_val = 0.0
        net_sent_val = 0.0

    return cpu_val, ram_val, disk_val, net_sent_val, net_recv_val, temp_val

# ========================
# FUNZIONE UPDATE PER GRAFICI
# ========================
def update(frame):
    t = time.time()
    cpu_val, ram_val, disk_val, sent_val, recv_val, temp_val = get_stats()

    timestamps.append(t)
    cpu_perc.append(cpu_val)
    ram_perc.append(ram_val)
    disk_perc.append(disk_val)
    net_sent.append(sent_val)
    net_recv.append(recv_val)
    cpu_temp.append(temp_val)

    # --- CPU ---
    axs[0].clear()
    axs[0].plot(timestamps, cpu_perc, color='blue')
    axs[0].set_ylabel("CPU %")

    # --- RAM ---
    axs[1].clear()
    axs[1].plot(timestamps, ram_perc, color='green')
    axs[1].set_ylabel("RAM %")

    # --- Disco ---
    axs[2].clear()
    axs[2].plot(timestamps, disk_perc, color='orange')
    axs[2].set_ylabel("Disk %")

    # --- Rete ---
    axs[3].clear()
    axs[3].plot(timestamps, net_sent, label='Sent KB')
    axs[3].plot(timestamps, net_recv, label='Recv KB')
    axs[3].legend()
    axs[3].set_ylabel("Net KB/s")

    # --- Temperatura CPU ---
    axs[4].clear()
    axs[4].plot(timestamps, cpu_temp, color='red')
    axs[4].set_ylabel("CPU Temp °C")
    axs[4].set_xlabel("Time (s)")

# ========================
# CREAZIONE FIGURA E SUBPLOT
# ========================
fig, axs = plt.subplots(5, 1, sharex=True, figsize=(10, 8))
fig.tight_layout(pad=2)

ani = FuncAnimation(fig, update, interval=1000, cache_frame_data=False)
plt.show()

# ========================
# CHIUSURA CONNESSIONE SSH
# ========================
ssh.close()
