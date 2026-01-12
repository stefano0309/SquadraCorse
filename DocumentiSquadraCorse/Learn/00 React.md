# 00 React

- Come creare e annidare i componenti
- Come aggiungere markup e stili
- Come visualizzare i dati
- Come rendere condizioni ed elenchi
- Come rispondere agli eventi e aggiornare lo schermo
- Come condividere i dati tra i componenti

### Creazione e annidamento di componenti

Le app che utilizzano React sono constituite da componenti. Ogni componente è una parte dell'interfaccia utente UI dotata di na propria logica e di un proprio aspetto.

I componeneti React sono funzioni JavaScript che restituiscono il markup:
```jsx
function MyButton() {
    return (
        <button>I'm a button</button>
    );
}
```

Ora possiamo annidare il componente MyButton in un altro componente:

```jsx
export default function MyApp() {
    return (
        <div>
            <h1>Welcome to my app</h1>
            <MyButton />
        </div>
    )
}
```

MyButton inizia con la lettera maiuscola siccome ogni componente React devono sempre iniziare con la lettera maiscola mentre i tag HTML devono avere la lettera minuscola

### Scrivere markup con JSX

La sintassi sopra viene chiamata jsx la maggiorparte dei progetti React lo usano per praticita questo linguaggio è molto più rigido di HMTL di fatto bisogna qiudere ogni tag come `<br />` e siccome si puo avere in `return` solo un elemento risogna racchiudere tutto all'interno di un div oppure di un wrapper `<>...</>` un tag vuoto.

### Aggiungere stili

In React si specifica una classe con `className` funziona allo stesso modo dell'attrivuto HTML `class`:

`<img className="avatar" />`

Per poi scrivere le regole CSS in un altro file nel caso più semplice per implementare css si utiizza `<link>` ma dipende dal framework che si sta utilizzando.

### Visualizzazione dei dati 

JSX consente di inserire markup in JavaScript le parentesi graffe consentono di incorporeare in una variabile dal codice e mostrarla all'utente 

```jsx
return (
    <h1>
        {user.name}
    </h1>
)
```

Possiamo anche utilizzare questi valori all'interno di alcuni elementi HTML per esempio per definire il percorso di un immagine:

```jsx
return (
    <img 
        className="avatar"
        scr={user.imageUrl}
    />
)
```

Possiamo anche inserire espressioni più complesse all'interno delle parentesi graffe JSX:

```jsx
const user = {
  name: 'Hedy Lamarr',
  imageUrl: 'https://i.imgur.com/yXOvdOSs.jpg',
  imageSize: 90,
};

export default function Profile() {
  return (
    <>
      <h1>{user.name}</h1>
      <img
        className="avatar"
        src={user.imageUrl}
        alt={'Photo of ' + user.name}
        style={{
          width: user.imageSize,
          height: user.imageSize
        }}
      />
    </>
  );
}
```

Nell'esempio sopra `style={{}}` non si tratta di una sintassi speciale ma di un `{}` oggetto normale racchiuso tra `style={}` parenttesi graffe JSX

### Rendering condizionale

In React esiste una sintassi specifica per scrivere le condizioni siutilizzano invece le stesse tecniche per scrivere codice JavaScript per esempio `if` 

```jsx
let content;
if (isLoggedIn) {
  content = <AdminPanel />;
} else {
  content = <LoginForm />;
}
return (
  <div>
    {content}
  </div>
);
```
In base alla condizione `isLoggedIn` si va  a mostrare una funzione che restituisce del codicce che viene assegnata a una variabile 

Volendo possiamo utilizzare una sintassi più semplice ma con lo stesso scopo utilizzando l'operatore condizionale `?`:
```jsx
<div>
    {isLoggedIn ? (
        <AdminPanel />
    ) : (
        <LoginForm />
    )}
</div>
```
Usiamo questo metodo se abbiamo bisogno di un else altimenti possiamo usare una sintassi logica più breve

```jsx
<div>
    {isLoggedIn && <AdminPanel />}
</div>
```

### Elenchi di rendering

Per visualizzaare gli elenchi dei componenti bisogna affidarae a un ciclo come for oppure a funzione degli array come `.map()`

Avendo una serie di elementi come:
```jsx
const products = [
    { title: 'Gabbage',id:1 }
    { title: 'Garlic',id:2 }
    { title: 'Apple',id:3 }
]
```

All'interno del componente si usa la funzione `.map()` per trasformare l'array in `<li>` articoli:

```jsx
const listItems = products.map(product =>
    <li key={product.id}>
        {product.title}
    </li>
);

return (
    <ul>{listItems}</ul>
);
```

Ogni elemento `<li>` utilizza una key che serve per identificarla univocamente normalmente dovrebbe essere un id

### Rispondere agli eventi

E possibile rispondere agli eventi dichiarando funzioni di gestione degli eventi all'interno dei componeti:

```jsx
function MyButton() {
    function handleClick() {
        alert('You clicked me!');
    }

    return (
        <button onClick={handleClick}>
            Click me
        </button>
    )
}
```

Non ci sono parentesi siccome React chiamera il gestore eventi quando l'utente clicca sul pulsante.

### Aggiornamento dello schermo

Spesso volendo utillizare i componenti memorizino alcune informazioni e le visualizzi per esempio per contare il numero di volte in cui un pulsante viene cliccato.

Per farlo aggiungiamo lo stato al componente:

`import { useState } from 'react';`

Ora dopo averlo importato possiamo dichiarere una variabile di stato all'interno del tuo componente:

```jsx
function MyButton() {
    const [count, setCount] = useState(0)
}
```
Otteremo due cose da `useState`: lo stato corrente `count` e la funzione di aggiornamento `setCount`.

Quindi la prima volta che verra visualizzato avrea `count` a 0 siccome abbiamo passato `useState()` a 0 quando vogliamo cambiare il suovalore chiamo `setCount` e passiamo il nuovo valore:

```jsx
function MyButton() {
    const [count, setCount] = useState(0)

    function handleClick() {
        setCount(count +1)
    }

    return (
        <button onClick={handleClick}>
            Clicked {count} times
        </button>
    )
}
```

### Utilizzo dei ganci

La funzione che inizializzo con `use` sono chiamate Hook. `useState` è un Hook integrato fornito da React si possono anche scrivere nuovi Hook combinando quelli esistenti.

Gli Hook sono più restritti delle funzioni puoi chiamare gli hook solo all'inizio dei tuoi componenti.

Se si vogliono utilizzarli `useState` in una consizione estrai un nuvo componente e lo si inserisce li.

### Condivisione dei dati tra i componenti

Nell'esmpio precedente ognino MyBtton aveva il suo indipendente count e quando cliccoo su ogni pulsante, count cambiava solo il valore del pulsante cliccato.

![esempio1](https://react.dev/_next/image?url=%2Fimages%2Fdocs%2Fdiagrams%2Fsharing_data_child.dark.png&w=828&q=75)

![esempio2](https://react.dev/_next/image?url=%2Fimages%2Fdocs%2Fdiagrams%2Fsharing_data_child_clicked.dark.png&w=828&q=75)

Ma ogni tanto si ha bisogno di componenti che condividano i dati e li aggiornino insieme.

Per far si che entrambi `MyButton` i componenti visualizzino lo stesso valore `count` e si aggiornino inseme è necessario spostare lo stato dai singoli pulsanti verso l'alto al componente più vicino che li contiene tutti

![esempio3](https://react.dev/_next/image?url=%2Fimages%2Fdocs%2Fdiagrams%2Fsharing_data_parent.dark.png&w=828&q=75)

![esempio4](https://react.dev/_next/image?url=%2Fimages%2Fdocs%2Fdiagrams%2Fsharing_data_parent_clicked.dark.png&w=828&q=75)

Quindi al clic, MyApp aggiorna il suo count stato di uno e lo passa a entrambi i figli  per fare cio bisogna sposate lo stato da MyButton a MyApp:

```jsx
export default function MyApp() {
  const [count, setCount] = useState(0);

  function handleClick() {
    setCount(count + 1);
  }

  return (
    <div>
      <h1>Counters that update separately</h1>
      <MyButton count={count} onClick={hadleCLick}/>
      <MyButton count={count} onClick={hadleCLick}/>
    </div>
  );
}

function MyButton({ count, onClick }) {
  return (
    <button onClick={onClick}>
      Clicked {count} times
    </button>
  );
}
```

E modifichima la funzion MyButton con dei parametri che vengono passati precedentemente tra le parentesi `{}`