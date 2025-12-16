import { useState, useEffect } from 'react';
import './style.css';
import React from 'react';

export default function App() {
  const [selector, setSelector] = useState(false);
  const [gamepad, setGamepad] = useState(null);
  const [vel, setVel] = useState(50);
  const [buttons, setButtons] = useState([])


  function handleChange(event) {
    const checked = event.target.checked;
    setSelector(checked);
    sendGamepadData(undefined, checked);
  }

  function btn() {
    const gp = navigator.getGamepads()[0];

    if (gp) {
      setGamepad(gp); // aggiorna lo state
      setButtons(
        gp.buttons.map(b => ({
          pressed: b.pressed,
          value: b.value
        }))
      );
    }

    requestAnimationFrame(btn);
  }


  useEffect(() => {
    btn()
  }, [])


  function sendGamepadData(gp = gamepad, currentSelector = selector, currentSpeed = vel) {
    const data = gp
      ? {
        Envirioment: {
          maxSpeed: currentSpeed
        },
        Setting: {
          mode: currentSelector ? "controller" : "volante",
          index: gp.index,
          id: gp.id,
          buttons: gp.buttons.length,
          axes: gp.axes.length,
        }
      }
      : {
        Envirioment: {
          maxSpeed: currentSpeed
        },
        Setting: {
          model: currentSelector ? "controller" : "volante",
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
              onChange={(e) => {
                const newVel = e.target.value;
                setVel(newVel);
                sendGamepadData(undefined, undefined, newVel);
              }}
            />
            <h3>{vel}</h3>
          </div>
        </form>
      </section>
      <section id='mapping'>
        {gamepad ? (
          <>
            <p><strong>Index:</strong> {gamepad.index}</p>
            <p><strong>ID:</strong> {gamepad.id}</p>
            <p><strong>Bottoni:</strong> {gamepad.buttons.length}</p>
            <p><strong>Assi:</strong> {gamepad.axes.length}</p>
            <div id="map">
              <div>
                <h3>CREA UNA CONFIGURAZIONE</h3>
                {buttons.map((btn, index) => (
                  <p key={index} className='p-mapping'>
                    <strong>Button ID {index}:</strong>{" "}
                    {btn.pressed ? "PREMUTO" : "RILASCIATO"}{" "}
                    <strong>Value:</strong>{"  "}
                    <input
                      type="text"
                      className="button-mapping"
                    />
                  </p>
                ))}
              </div>
              <div>
                <h3>CARICA UNA CONFIGURAZIONE</h3>
                <textarea id="text-area" placeholder="Scrivi qui..."></textarea>
              </div>
            </div>

          </>
        ) : (
          <p>{selector ? "Collega un controller" : "Collega un volante"}</p>
        )}
      </section>
    </>
  )
}
