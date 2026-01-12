
### Progetto

La **grafica** viene definita con HTML e CSS che vanno a  creare lo stile della pagina web che farà da GUI tramite poi Java Script leggiamo il controller che permette di leggere i valori degli assi quindi assi del volante e assi dei pedali.

A seconda di questi valori la GUI assume un aspetto diverso essa poi potrà essere modificata a seconda delle necessita essi poi vengono inviati al backend gestito da Python e WebSocket che serve per configurarlo come server.

Poi i valori inviati da Java Script verso il Raspberry vengono inviati tramite archivi JSON (più facili da gestire in python) e inviati con pacchetti UDP mentre i valori di latenza e telemetria cioè dal raspberry pi verso la GUI vengono analizzati e trattati dal Client python ovvero lo stesso raspberry pi li invia indietro.

Oppure possono essere inviati grezzi e poi rielaborati sulla macchina originaria che fa da server per il Raspberry e poi inseriti a schermo tramite il WebSocket di Python dove andranno poi a essere inseriti come grafici tabelle ecc...

Sarebbe bello ottenere quindi una GUI che presenta una rappresentazione dei comandi con sopra magari il video in ingresso della telecamera in caso non si voglia usare il visore 3D oppure usare il visore e averlo per chi guarda la gara.

### Elementi necessari

Quindi per la creazione della GUI base si possono usare semplici elementi si HTML e CSS come div arrotondati e forme semplici per creare la grafica del volante e dei pedali come per il controller di esempio

![[Pasted image 20251209091044.png]]

Ma per il volante per poi mappare assi e tasti tramite JavaScript

```js
const gp = navigator.getGamepads()[0];
```

Che ci permette di vedere i controller collegati poi mappare inizialmente gli assi poi si può semplificare la mappatura tramite magari un JSON letto da python e i valori inviati alla pagina in  modo da semplificare la logica e l'eventuale modifica.

Essa inizialmente veniva svolta tramite Pygame ma utilizzando quel metodo bisognava eseguire troppi script contemporaneamente che rendono molto piu difficile l'esecuzione del programma avevamo:
- UDP.py che inviava i dati verso
- GUI.py che creava una grafica bruttina con elementi semplici di Pygame
- Ping.py che misurava la latenza
- PyClient.py che misura i vari valori del raspberry pi
- Ps4Controller.py che conteneva la classe che definiva i metodi del controller  e della lettura dei tasti
- ServerUDP.py creato direttamente sul raspberry pi che rielabora i dati in un archivio JSON e usa GPIO per la rielaborazione dei dati e l'esecuzione dei vari motori quello dello sterno e quello del motore principale