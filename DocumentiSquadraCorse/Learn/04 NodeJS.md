## Cos'è Node.js
Non è un lingaggio di programmazione ma un runtime che consente di eseguire JavaScript su un server.

Apparso per la prima volta negli anni '90 precedentemente esistva PHP invece ora con Node.js permette di creare full stack application con un singolo linguaggio di programmazione

## Cosa può fare Node

Quindi visitando un URL su internet che punta al server effettuat alrm richiesta il server la elaborame risponde al client:

**Installare Node:**
 
Esso può essere installlato su Windows linux Mac controlliamo la verione con `node -v` e cui possiamo installare nuove versioni 

Se apriamo il terminale ed eseguiamo il comando `node` possiamo eseguire codice javascript direttamente nel terminale

Possiamo poi andare a creare un `index.js` ed eseguirlo con `node` con il comando `node .` cosi facendo possiamo avere il risulatato del nostro codice JavaScript nel terminale al posto di dover andare ad aprire il browser

## Tempo di esecuzione con node

```js
//console.log('Ciao mondo 👋')
/*
console.log(global.luckyNum);

global.luckyNum = '23';

console.log(global.luckyNum)
*/

console.log(process.platform); //vede su che sistema siamo
console.log(process.env.USER); //vede l'utente
```

### Eventi

Come funzionano gli eventi in Node.js molto spesso descrito  come n runtime javascript asincrono guidato da eventi il runtime implementa chiamata event loop che permette di separare quindi solo operazioni non bloccanti molto veloci si verificano prorpio per questo node non bloccantte.

## File System

```js
const { readFile } = require('fs')

readFile('./hello.txt', 'utf8', (err,txt) => {
    console.log(txt)
});

console.log('fai queesto al più presto')
```

## Esempio applicazione

Utilizzo la funzione `node init -y` per creare il file di configurazione dell'ambiente successivamente andare ad installare `express` con `npm install express`

```js
const express = require('express');
const { readFile } = require('fs');

const app = express();

app.get('/', (request, response) => {

    readFile('./home.html', 'utf-8', (err, html) => {
        if (err) {
            response.status(500).send('Fuori servizio')
        }
        response.send(html)
    })
});

app.listen(process.env.PORT || 3000 , () => console.log('App funzionante su http://localhost:3000'))
```

Eseguiamo lo Sript con `node .`