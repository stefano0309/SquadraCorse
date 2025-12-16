import { useState, useEffect } from 'react';
import './style.css';

export default function App() {
  const [selector, setSelector] = useState(false); // false = volante, true = controller
  const [gamepad, setGamepad] = useState(null);
  const [vel, setVel] = useState(50);

  // Gestione checkbox
  function handleChange(event) {
    const checked = event.target.checked;
    setSelector(checked);
    sendGamepadData(gamepad, checked);
  }

  // Invio dati al backend
  function sendGamepadData(gp, currentSelector = selector) {
    const data = gp
      ? {
          Setting: {
            type: !currentSelector ? "controller" : "volante",
            index: gp.index,
            id: gp.id,
            buttons: gp.buttons.length,
            axes: gp.axes.length,
          },
        }
      : {
          Setting: {
            type: !currentSelector ? "controller" : "volante",
            index: null,
            id: null,
            buttons: null,
            axes: null,
          },
        };

    console.log("Dati inviati al backend:", data);

    fetch('http://localhost:3000/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
      .then(res => res.ok ? console.log("POST riuscita") : console.error("Errore invio dati"))
      .catch(err => console.error("Errore fetch:", err));
  }

  // Gestione gamepad connesso
  useEffect(() => {
    function handleGamepadConnected(e) {
      const gp = navigator.getGamepads()[e.gamepad.index];
      console.log("Gamepad connesso:", gp);
      setGamepad(gp);
      sendGamepadData(gp);
    }

    window.addEventListener("gamepadconnected", handleGamepadConnected);
    return () => window.removeEventListener("gamepadconnected", handleGamepadConnected);
  }, []);

  return (
    <>
      <header>
        <nav>
          <h1>🚙 Progetto Corse</h1>
          <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#impostazioni">Impostazioni</a></li>
            <li><a href="#start">Start</a></li>
          </ul>
        </nav>
      </header>

      <section id="home">
        <h2>Controllo macchina tramite volante o controller</h2>
        <form>
          <div className='inputSelection'>
            <h4>VOLANTE</h4>
            <label className="switch">
              <input
                type="checkbox"
                checked={selector}
                onChange={handleChange}
              />
              <span className="slider round"></span>
            </label>
            <h4>CONTROLLER</h4>
          </div>

          {selector ? (
            <div className="controller">
              <h3>Modalità controller</h3>
              <p>Andiamo a creare una mappatura del tuo controller</p>
            </div>
          ) : (
            <div className="volante">
              <h3>Modalità volante</h3>
              <p>Andiamo a creare una mappatura del tuo volante</p>
            </div>
          )}

          <div className="inputSelection">
            <label htmlFor="velSlider">Velocità massima:</label>
            <input 
              type="range" 
              id="velSlider"
              min="1"
              max="100"
              value={vel}
              onChange={(e) => setVel(e.target.value)}
            />
            <h3>{vel}</h3>
          </div>
        </form>
      </section>

      <section id='map'>
        {gamepad ? (
          <>
            <p><strong>Index:</strong> {gamepad.index}</p>
            <p><strong>ID:</strong> {gamepad.id}</p>
            <p><strong>Bottoni:</strong> {gamepad.buttons.length}</p>
            <p><strong>Assi:</strong> {gamepad.axes.length}</p>
          </>
        ) : (
          <p>{selector ? "Collega un controller" : "Collega un volante"}</p>
        )}
      </section>
    </>
  );
}
