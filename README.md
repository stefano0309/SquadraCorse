Il progetto è attualmente suddiviso in tre macrocategorie:

**1. Codice Python (PC / Raspberry Pi)**  
Si occupa di:

- Mappare, riconoscere e normalizzare i comandi provenienti da controller o volante.
- Stabilire la comunicazione seriale con il trasmettitore.
- Avviare una fase di _handshake_ durante la quale:
    - viene comunicato quale modulo radio è in uso (2.4 GHz oppure 433 MHz);
    - viene definita la frequenza di invio dei pacchetti (pacchetti al secondo);
    - nel caso del 433 MHz, viene impostata anche la potenza di trasmissione.

Il software legge continuamente gli input e li converte in un comando compatto da inviare via seriale al trasmettitore. Il pacchetto è strutturato nel seguente modo:

- 1 byte per lo sterzo
- 1 byte per l’accelerazione
- 1 byte per il freno
- 1 bit per la retromarcia
- 3 bit riservati per implementazioni future
- 4 bit per la selezione della velocità (valore compreso tra 1 e 16; il numero effettivo di velocità può essere modificato)
- 2 byte di CRC (Cyclic Redundancy Check), indispensabili per rilevare eventuali errori dovuti a interferenze o rumore, che potrebbero compromettere il funzionamento del motore o danneggiare componenti meccaniche.

---

**2. Codice C per il Trasmettitore**

Il firmware del trasmettitore:

- Riceve i comandi dal PC o dal Raspberry Pi tramite seriale.
- Verifica l’integrità del pacchetto controllando la CRC.
- Aggiunge 4 byte di token identificativo (VAL1) all’inizio del comando.
- Trasmette il pacchetto tramite il modulo radio collegato.

Il modulo radio può essere cambiato in qualsiasi momento (2.4 GHz o 433 MHz) senza necessità di riavviare le schede (hot swap).

---

**3. Codice C per il Ricevitore**

Il firmware del ricevitore:

- Riceve i pacchetti tramite il modulo radio collegato.
- Verifica che il token di identificazione corrisponda.
- Controlla la validità dei dati tramite CRC.
- Se il pacchetto è valido, esegue il comando: sterzo, accelerazione, freno e retromarcia.
- La gestione della velocità impostata è ancora da implementare.