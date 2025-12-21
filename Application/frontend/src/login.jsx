import AdminPanel from './AdminPanel/adminPanel';
import ClientPanel from './ClientPanel/clientPanel';
import { useState, useEffect } from 'react';
import './style.css'



export default function Login({ setLogin, login }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [selector, setSelector] = useState(false);
    const [admin, setAdmin] = useState(false)
    const [client, setClient] = useState(false)

    function sendCredentials() {
        const data = {username};

        fetch('http://localhost:3000/credential', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data),
        })
            .then(res => res.ok ? console.log("POST riuscita") : console.error("Errore invio dati"))
            .catch(err => console.error("Errore fetch:", err));
    }

    function handleLoginAdmin() {
        if (!admin){
            setAdmin(true)
            setClient(false)
        }
        else{
            if (username === 'admin' && password === '1234') {
                setLogin('admin');
                setUsername('')
                setPassword('')
            } else if (username !== '' && password !== '') {
                alert('Credenziali Admin errate');
                setUsername('')
                setPassword('')
            }
            setAdmin(false)
        }
    }

    function handleLoginClient() {
        if (!client){
            setClient(true)
            setAdmin(false)
        }
        else{
            if (username !== '') {
                setLogin('client');
                sendCredentials();
            }
            setUsername('')
            setClient(false)
        }
    }

    return (
        <>
            {login == '' && (
                <div className="wrapper">
                    <div className="login-form">
                        <button onClick={handleLoginAdmin}>Accedi come admin</button>
                        {admin && (
                            <>
                                <label>Username</label>
                                <input
                                    type="text"
                                    placeholder="userName"
                                    value={username}
                                    onChange={e => setUsername(e.target.value)}
                                />
                                <label>Password</label>
                                <input
                                    type="password"
                                    placeholder='password'
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                />

                            </>
                        )}
                        <button onClick={handleLoginClient}>Accedi come client</button>
                        {client && (
                            <>
                                <label>Username</label>
                                <input
                                    type="text"
                                    placeholder="userName"
                                    value={username}
                                    onChange={e => setUsername(e.target.value)}
                                />
                            </>
                        )}
                    </div>
                </div>
            )}

            {login == 'admin' && (
                <AdminPanel selector={selector} setSelector={setSelector} />
            )}

            {login == 'client' && (
                <ClientPanel selector={selector} />
            )}
        </>
    )
}