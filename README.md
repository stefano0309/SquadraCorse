# 🏎️ SquadraCorse

## 🎯 Obiettivo
Creare un’interfaccia che permetta la visualizzazione dei comandi e delle impostazioni di comunicazione di un sistema remoto.
L’interfaccia consente di controllare una macchina radiocomandata (sviluppata negli anni precedenti) tramite un volante o un controller connesso via cavo al computer. La comunicazione tra il computer e la macchina avviene tramite segnali radio.

## 🧩 Descrizione del progetto
Il frontend è sviluppato con il framework React, mentre il backend utilizza Node.js e API per gestire la comunicazione tra interfaccia, controller e volante.

È possibile mappare direttamente i controlli dal sito, così da adattare il sistema a diversi modelli di controller o volanti.
La lettura dei pulsanti e degli assi viene eseguita dal browser; il sistema associa semplicemente nomi ai valori in ingresso, in base alle variazioni dei comandi.

È inoltre presente una pagina di login di base, che distingue l’accesso tra utenti admin e client.

## 🛠️ Tecnologie utilizzate
- React
- Node.js
- CSS3

## ⚙️ Dettagli tecnici
La comunicazione avviene tra:

- Il computer principale, che gestisce l’interfaccia utente, l’analisi dei comandi e la connessione con i controller;
- Un Raspberry Pi installato sulla macchinina, che gestisce la telemetria in tempo reale, la trasmissione dei dati e il controllo dei motori.

Questa architettura consente un flusso di dati bidirezionale e una risposta immediata ai comandi inviati dal controller.