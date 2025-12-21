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
                        <li><button>Impostazioni</button></li>
                        <li><button>Start</button></li>
                    </ul>
                </nav>
            </header>
        </>
    )
}