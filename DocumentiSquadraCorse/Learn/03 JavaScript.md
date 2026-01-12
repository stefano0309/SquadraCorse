## Cos'è JavaScript

- **E un linguaggio interpretatoto ad alto livello**
Non bisogna andare ad un livello hardware come un basso livello ed essendo interpretata non ha bisogno di un intereprete
- **Conforme alle specifiche ECMAScript**
- **Multi-paradigma**
Vuol dire che possiamo scrivere object-oriented o in altri modi
- **Funziona sia su browser che su server Node.js**

## Perchè imparare JavaScript

- Sdiccome è il linguaggio del browser mentre comepython non possono interagire direttamente con iol web
- Si possono creare interfacce con TEact
- Possiamo costruire molto velocemente un'applicazione fulll stack
- Usato per lo sviluppoo mobile
- Usato per applicazioni desktop 

Possiamo inserire javascript direttamente nel file html oppure in un file separato.

Esso dev'essere inserito al fondo della pagina in modo che venga caricato prima html o css.

Possiamo inviare valori alla console della pagina tramite:
```js
conosle.log('Ciao mondo!') //Invia la stringa in conosole
```

### Variabili
Ci sono 3 modi per creare delle variabili var,let,const 
var -> globali meglio non usarle
let -> possiamo riassegrare il valore
const -> non possiamo riassegnare il valore siccome è una costante

### Tipi di dati di base

- String
- Numbers
- Boolean
- null
- undefined
- Symbol


```js
const name = 'John';
const age = 30;
const rating = 4.5; //non esiste un vero e proprio tipo per le decimali
const isCool = true;
const x = null; //-> Ci da object ma è un vecchio errore di javascript
const y = undefined;
let z;

//Testiamo il tipo di dato con con typeof  
```

## Stringhe

**Concatenazione**

```js
const name = 'John';
const age = 30;

//Concatenazione
console.log('My anme is '+name+' and I am '+age)
//Template String
console.log(`My name is $(name) and I am $(age)`)
```

**Metodi e propieta stringhe**
- Metodo ha le parentesi
- Proprieta non ha le parentesi

```js
const s = 'John';

//Lunghezza di una parola 
console.log(s.length)
//MEtodo per fare la stringa tutta in maiuscilo o tutto minuscolo
console.log(s.toUpperCase()); //metodo
console.log(s.toLowerCase());
//Sottostringhe
console.log(s.substring(0,2));
//String to array
console.log(s.split('')); //Divide per i caratteri se non mettiamo nulla
```

## Commenti

// linea singola
/*multi riga */

## Arrays

**Variabili che contengono valori mltipli**

```js
const numbers = new Array(1,2,3,4,5) // con new sono dei costrutti
console.log(numbers);

const fruits = ['Apples', 'oranges','pears'] //dichiarazione molto semplice 
console.log(fruits);

//Acedere a un valore specifico
console.log(fruits[1]); //-> oranges 

fruits[3] = 'grapes';
console.log(fruits [3]); //-> grapes aggiunge al fondo

//Aggiungere elementi a un array
fruits.push('mangos'); //Aggiunge al fondo 

fruits.unshift('strawberries'); //Aggiunge all'inizio

//Eliminare elementi da un array 
fruits.pop(); //elimina il primo elemento

//Controllare se qualcosa è un array
console.log(Array.isArray('Hello')); //->false non è un array

//Trovare l'indice di un elemento
console.log(fruits.indexOf('oranges'));
```

## Object literal

```js
const person = {
    firstName: 'John',
    lastName: 'Doe',
    age: 30,
    hobbies: ['music','movies','sports']
    adress: {
        street: '50 main st',
        city: 'Boston',
        state: 'MA'
    }
}


// Cercare un valore al suo interno
console.log(person.firstName, person.lastName)

//Accedere a un valore a ll'interno che è un array e accedee al elemento
console.log(person.hobbies[1])

//Accedere all'interno dell'oggetto che contiene un altro oggetto
console.log(person.adress.city)

/*Possiamo anche assegnare a delle variabili il valore effettivo 
dell'oggetto che andiamo a  cercare*/

const { firstName, lastName } = person;

console.log(firstName) //-> John

//Possiamo anche aggiungere proprieta
person.email = 'john@gmail.com' 
```

## Array di object literal

```js
const todos = [
    {
        id: 1,
        text: 'Take out trash',
        isCompleted: true
    }
    {
        id: 2,
        text: 'Meeting with boss',
        isCompleted: true
    }
    {
        id: 3,
        text: 'Dentist appt',
        isCompleted: false
    }
];

// convertire in json

const todoJSON = JSON.stringify(todos);
console.log(tosoJSON);
```

## Cicli

```js
// For
for(let i  = 0; i<10; i++){
    console.log('i');
}

// While
let i = 0;
while(i<10){
    console.log(i);
    i++;
}
```

```js
// For casi particolari
const todos = [
    {
        id: 1,
        text: 'Take out trash',
        isCompleted: true
    }
    {
        id: 2,
        text: 'Meeting with boss',
        isCompleted: true
    }
    {
        id: 3,
        text: 'Dentist appt',
        isCompleted: false
    }
];

// cicla per il numero di elementi contenuti in todos -> 3
for (let i = 0; i<todos.lenght; i++){
    console.log(todos[i].text);
}

for (let todo of todos){
    console.log(todo.text)
}

// forEach, map, filter

//Loop per variabile 
todos.forEach(function(todo){
    console.log(todo.text)
})

//Ci da un array in ritorno con solo gli elementi che vogliamo
const todoText = todos.map(function(todo){
    return todo.text;
})

//aggiuge a una array secondo uan condizione
const todoCompleted = todos.filter(function(todo){
    return todo.isCompleted === true;
})

//Possiamo anche concatenare questi metodi
const todoCompleted = todos.filter(function(todo){
    return todo.isCompleted === true;
}).map(function(todo){
    return todo.text; //array dei testi dei todos che sono completati
})
```

## Condizioni

```js
const x = 10;
// === guarda anche il tipo  == mentre questo no
if(x == 10){
    console.log('x is  10');
}else if(x>10){
    console.log('x è maggiore di 10')
}else{
    console.log('x is not 10')
}
```

Per gli operatori booleani:
- OR || 
- AND &&
- NOT !

```js
const x = 4;
const y = 10;

if (x>5 || y>10){
    console.log('x è maggioe di 5 oppure y e maggiore di 10')
}
```

Possiamo avere anche degli if in riga molto usato per dare il valorea  a una variabile in basae a una condizione

```js
const x =10;

const color = x > 10 ? 'red' : 'blue' //il primo se vero il secondo se falso

switch(color){
    case 'red':
        console.log('Il colore è rosso');
        break;
    case 'blue':
        console.log('Il colore è blu');
        break;
    default:
        console.log('Il colore non è ne rosso ne blu');
        break;
}
```

## Funzioni

```js
function addNums(num1 = 1, num2  = 2) { //nome funzione e parametri
    console.log(num1 + num2); //Istruzioni
}

addNums(5,5); //richiamo la funzione 
//Posso avere dei valori di base per i parametri che vanno a essere sovrascritti
//Con i nuovi
```

```js
const addNums = (num1 =1, num2 = 2) => {
    return num1 + num2
}
addNums(5,5)
```

## OOP

Possiamo andarea a crearea oggetti con i costrutti interni oppure con le classi

```js
//funzione costruttiva
function Person(firstName, lastName, dob) {
    this.firstName = firstName;
    this.lastName = lastName;
    this.dob = new Date(dob);
}

//istanzionamento dell'oggetto
const person1 =  new Person('John' 'Doe', '4-3-1980') 
// Possiamo far passarea la data come un oggetto data 

console.log(person1)
console.log(person1.dob.getFullYear())
```

Possiamo anche creare metodi personalizzati per i nostri oggetti

```js
function Person(firstName, lastName, dob) {
    this.firstName = firstName;
    this.lastName = lastName;
    this.dob = new Date(dob);
    this.getBirthYear = function(){
        return this.dob.getFullYear();
    }
    this.getFullName = function(){
        return  `$(this.firstName) $(this.lastName)`;
    }
}

//istanzionamento dell'oggetto
const person1 =  new Person('John' 'Doe', '4-3-1980') 
// Possiamo far passarea la data come un oggetto data 

console.log(person1)
console.log(person1.dob.getFullYear())
```
Questo modo no è il miglior moto per creare dei metodi quindi possiamo usare `.prototype` in modo da avere l funzione costruttrice 
il piu pulita possibile siccome non è detto che andremo ami ha usarli tutti 

```js
function Person(firstName, lastName, dob) {
    this.firstName = firstName;
    this.lastName = lastName;
    this.dob = new Date(dob);
}

Person.prototype.getBirthYear = function() {
    return this.dob.getFullYear();
}

Person.prototype.getFullName = function() {
    return  `$(this.firstName) $(this.lastName)`;
}

const person1 =  new Person('John' 'Doe', '4-3-1980') 

console.log(person1.getFulName());
console.log(person1);
```

## Classi

```js
class Person {
    constructor(firstName, lastName, dob) {
        this.firstName = firstName;
        this.lastName = lastName;
        this.dob = new Date(dob);
    }

    getBirthYear() {
        return this.dob.getFullYear();
    }

    getFullName() {
        return  `$(this.firstName) $(this.lastName)`;
    }
}

const person1 = new Person('jonh', 'Doe', '4-3-1980')

console.log(person1)
```

## Document Object Module

Possiamo avere selettori singoli e selettori multipli per vedere le proprieta dello schermo `console.log(window)`

```js
//Elementi singoli
document.getElementById('my-form')

//Elementi multipli
console.log(document.querySelectorAll('.item'))
console.log(document.getElementsByClassName('item'))
console.log(document.getElementsByTagName('li'))
```

Metodi sugli elementi del DOM

```js
const ul = document.querySelector('.items');

ul.remove(); //rimuove l'intero elemento
ul.lastElementChild.remove(); //Rimuove l'elemento figlio 
ul.firstElementChild.textContent = 'Hello'; // Cambia il contenuto 
//del primo elemento figlio
ul.children[1].innerText = 'Brad'; //Cambia il contenuto del elemento
//  indicato con l'indice
ul.lastElementChild.innerHTML = '<h4>Hello</h4>'; //Cambia HTML 
// interno all'elemento
```
Possiamo cambiare anche lo stile dell'elemento del DOM

```js
const btn = document.querySelector('.btn');
btn.style.background = 'red';
```

Possiamoa anche ad andare a definire delle azioni in caso di particolari eventi che avvengo sull'elemento

```js
const btn = document.querySelector('.btn');

btn.addEventListener('click', (e) => {
    e.preventDefault(); //Previene lo stop dell'evento
    document.querySelector('#my-form').style.background = '#ccc' 
    // Definisce lo stile del background
    document.querySelector('body').classList.add('bg-dark'); 
    // Aggiunge una classe a un elemento 
    document.querySelector('.items').lastElementChild.innerHTML = '<h1>Hello</h1>'
})
```

Esempio di un eventuale form di una pagina di logic in cui viene fato vedere errore se non completiamo l'intero form e scrive all'interno dello schermo nome ed email precedentemente inserito nel form 

```js
const myForm = document.querySelector('#my-form');
const nameInput = document.querySelector('#name');
const emailInput = document.querySelector('#email');
const msg = document.querySelector('.msg');
const userList = document.querySelector('#users');

myForm.addEventListener('submit', onSubmit);

function onSubmit(e) {
    e.preventDefault();

    if (nameInput.value === '' || emailInput.value === ''){
        msg.classList.add('error')
        msg.innerHTML = 'Perfavore compilare tutto il modulo';
        setTimeout(() => msg.remove(), 3000);
    }else{
        const li = document.createElement('li');
        li.appendChild(document.createTextNode(`${nameInput.value} :
            ${emailInput.value}`
        ));

        userList.appendChild(li);
        nameInput.value  ='';
        emailInput.value = '';
    }
}
```