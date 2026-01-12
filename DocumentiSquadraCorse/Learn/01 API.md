# API

L' API è un modo di comunicare tra di loro per due  computer per esmpio possiamo prendere il sito della Nasa e vedere il loro programma sugli asteroidi oppure usare l'API rest della pagina per ottenere i dati JSON visualizzati sullo schermo

## API RESTful

Ovvero che seguono una serie di regole o vincoli noti come trasferimento di stato rappresentativo esso organizzà dati ed entità di dati o risorse in gruppi di URL univoci non proprio degli URL ma URL o identificatori uniforni di risorse che identificano diversi tipidi risorse di dati su server.

Quindi un Client puo effetuare una richiesta a tale endpoint tramite HTTP il formato di richiesta è molto specifico la prima riga indica l'URL a cui si vuole accedere preceduto da un metodo o un verbo HTTP che segnala l'intento.

esempio:

```http
POST /dinosaur

Accept:application/json
Authorization: <token>
Connection: keep-alive

{
    "face":"🐊"
}
```

- GET -> Leggere
- POST -> Creare una nuova risorsa
- PATCH -> Per gli aggiornamenti
- DELETE -> Per rimuovere i dati 

Sotto la prima riga ritroviamo dei metadati sulla richiesta per esempio:
  
- Accept può indicare al server il fatto che vogliamo solo elementi JSON

Infiene in fondo troviamo il corpo che contiene un payload personalizzato di richiesta quindi ed eseguira del codice per leggere da un database che può quindi essere formattato in un messaggio di risposta.

Il messaggio di risposta contiene un codice si stato per dire al client cosa è successo alla sua richiesta in genere in codici 
- 200 vuol dire che è andato tutto bene
- 400 significa che qualcosa non andava nella richiesta
- 500 il Server a fallito 

Dopo il codice di stato abbiamo gli headers di risposta che contengo informazioni sul server.

Infine il corpo della risposta che contiene il playload dei dati ed è solamente formattato in JSON viene usata un architettura STATELESS il che significa che le due parti non hanno bisogno di memorizzare alcuna informazione l'una sull'altra e

## Creare un API con node js

Il modo più veloce per anadare a creare API restfull è express.js