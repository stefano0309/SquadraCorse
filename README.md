# 🏎️ SquadraCorse

## 🎯 Obiettivo
Creare una console app che permetta la visualizzazione dei comandi e delle impostazioni di comunicazione di un sistema remoto.
L’interfaccia consente di controllare una macchina radiocomandata (sviluppata negli anni precedenti) tramite un volante o un controller connesso via cavo al computer. La comunicazione tra il computer e la macchina avviene tramite segnali radio.

## 🧩 Descrizione del progetto
Il progetto è sviluppato grazie al utilizzo di Python che permette di leggere gli input del volante 


## 🛠️ Tecnologie utilizzate
-Python

## ⚙️ Dettagli tecnici
La comunicazione avviene tra:

- Il raspberryPi5 che gestisce l'applicativo console e la comunicazione in invio per i comandi e in ricezione per la telemetria
- ES32 ricezione dei dati inviati dal raspberry ed invio della telemetria

## Utilizzo

1. Creare un ambiente virtuale
Dalla root della repository (SquadraCorse/):

Linux / macOS
python3 -m venv .venv

Windows
python -m venv .venv


2. Attivare l’ambiente virtuale

Linux / macOS
source .venv/bin/activate

Windows (PowerShell)
.venv\Scripts\activate


Dopo l’attivazione, vedrai il prompt modificato così:

(.venv) $


3. Installare le dipendenze

pip install -r requirements.txt


4. Eseguire il programma
⚠️ Da root della repo, non entrare in src/:

python -m src.main


Questo comando avvia il programma e permette a Python di trovare correttamente i moduli.

5. Uscire dal programma

Chiudi la finestra o premi ESC / pulsanti previsti nel menu.
