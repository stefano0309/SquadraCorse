import AdminPanel from './adminPanel';
import ClientPanel from './clientPanel';
import { useState, useEffect } from 'react';
import './style.css'



export default function Login({ setLogin, login }) {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    function handleLoginAdmin() {
        if (username === 'admin' && password === '1234') {
            setLogin('admin');
            setUsername('')
            setPassword('')
        } else {
            alert('Credenziali Admin errate');
            setUsername('')
            setPassword('')
        }
    }
    function handleLogin() {
        setLogin('client')
    }


    return (
        <>

            {login == '' && (
                <div className="wrapper">
                    <div className="login-form">
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
                        <button onClick={handleLoginAdmin}>Accedi come admin</button>
                        <button onClick={handleLogin}>Accedi come client</button>
                    </div>
                </div>
            )}

            {login == 'admin' && (
                <AdminPanel />
            )}

            {login == 'client' && (
                <ClientPanel />
            )}

        </>
    )
}