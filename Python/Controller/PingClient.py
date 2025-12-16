import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from random import randint  # sostituire con ping_host

# --- Liste dati ---
time_vals = []
min_vals = []
medium_vals = []
max_vals = []

# --- Funzione ping_host ---
def ping_host(ip):
    return randint(10, 50), randint(50, 100), randint(100, 200)

# --- Funzione di aggiornamento ---
def update(frame):
    min_val, medium_val, max_val = ping_host("192.168.1.234")
    time_vals.append(len(time_vals))
    min_vals.append(min_val)
    medium_vals.append(medium_val)
    max_vals.append(max_val)

    axs[0].clear()
    axs[0].plot(time_vals, min_vals, color="green")
    axs[0].set_ylabel("Min (ms)")
    axs[0].set_title("Ping Min")

    axs[1].clear()
    axs[1].plot(time_vals, medium_vals, color="orange")
    axs[1].set_ylabel("Medium (ms)")
    axs[1].set_title("Ping Medium")

    axs[2].clear()
    axs[2].plot(time_vals, max_vals, color="red")
    axs[2].set_ylabel("Max (ms)")
    axs[2].set_xlabel("Time (s)")
    axs[2].set_title("Ping Max")

# --- Funzione per salvare l'immagine quando la finestra viene chiusa ---
def on_close(event):
    fig.savefig("ping_monitor.pdf")
    print("Grafico salvato come ping_monitor.pdf")

# --- Creazione figura con 3 subplot ---
fig, axs = plt.subplots(nrows=3, ncols=1, sharex=True, figsize=(8,6))
fig.tight_layout(pad=3)

# Collego l'evento di chiusura
fig.canvas.mpl_connect('close_event', on_close)

ani = FuncAnimation(fig, update, interval=1000)
plt.show()
