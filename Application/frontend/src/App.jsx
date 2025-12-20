import './style.css';
import { useState } from 'react';
import Menu from './menu.jsx'
import Login from './login.jsx'

export default function App() {
  const [login, setLogin] = useState('');

  return (
    <>
      <Menu setLogin={setLogin} />
      <Login setLogin={setLogin} login={login} />
    </>
  )
}
