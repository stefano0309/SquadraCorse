# Squadra Corse Vallauri

![Logo IIS Vallauri ](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR5ArEsCuGnQMDTdWn5Vb-JK_nA8KyLcBEyjA&s)

## Obiettivo
Creare una console app che permetta la visualizzazione dei comandi e delle impostazioni di comunicazione di un sistema remoto.
L’interfaccia consente di controllare una macchina RC (sviluppata negli anni precedenti) tramite un volante o un controller connesso via cavo al computer. La comunicazione tra il computer e la macchina avviene tramite segnali radio.

## Descrizione del progetto
Il progetto è sviluppato grazie al utilizzo di Python che permette di leggere gli input del volante e tramite un ESP32 montato sulla macchina che riceve i dati dal computer principale e da i segnali rispettivi alla macchina


## Tecnologie utilizzate
- Python
- Arduino

## Dettagli tecnici
La comunicazione avviene tra:

- Il RaspberryPi5 che gestisce l'applicativo console e la comunicazione in invio per i comandi e in ricezione per la telemetria
- ESP32 ricezione dei dati inviati dal raspberry ed invio della telemetria

## Utilizzo

Guardare la wiki nella sezione [[Installazione]] per installare e configurare le dipendenze necessarie.
