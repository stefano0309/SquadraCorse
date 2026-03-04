# 🏎️ Guida al Setup Programma SquadraCorse
Segui questa procedura in ordine cronologico per garantire il corretto funzionamento della vettura e del software.

## 1. Preparazione Hardware
Kit: Preleva il kit hardware contrassegnato dal numero identificativo della tua macchina.

Alimentazione: Accendi il Raspberry Pi corrispondente.

Directory di lavoro: Apri il terminale e spostati nella cartella principale:

```Bash
cd ~/SquadraCorse
```
## 2. Gestione Repository (Git)
Assicurati che il codice sia aggiornato e di lavorare sul ramo corretto per i test.

Aggiornamento locale:

```Bash
git pull
```
Verifica Branch: Controlla il branch attuale con git branch.

Se sei già su TestCostamagna, procedi al punto successivo.

Se sei su un altro branch, esegui lo switch:
```Bash
git checkout TestCostamagna
```
## 3. Configurazione Ambiente Virtuale (Python)
È fondamentale isolare le dipendenze per evitare conflitti di sistema.

Creazione Ambiente (se non esiste):

```Bash
python3 -m venv .venv
```
Attivazione:

```Bash
source .venv/bin/activate
```
Nota: Una volta attivato, vedrai (.venv) all'inizio della riga di comando.

## 4. Esecuzione Software
Spostati nel cuore del progetto ed avvia lo script principale:

```Bash
cd Python/src
python main.py
```

## 5. Eseguibile ambiente 

```BASH
chmod +x setup_corse.
```

```BASH
./setup_corse.sh
```