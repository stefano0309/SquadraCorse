import './style.css'


export default function Menu({ setLogin }) {

    function handleHome() {
        setLogin('')
    }

    return (
        <>
            <header>
                <nav>
                    <h1>🚙 Progetto Corse</h1>
                    <ul>
                        <li><button onClick={handleHome}>Login</button></li>
                        <li><a href="#impostazioni">Impostazioni</a></li>
                        <li><a href="#start">Start</a></li>
                    </ul>
                </nav>
            </header>
        </>
    )
}