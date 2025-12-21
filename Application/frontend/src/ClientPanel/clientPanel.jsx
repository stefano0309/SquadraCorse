import '../style.css'

export default function ClientPanel({selector}) {

    return (
        <>
            <section>
                {selector ? <h2>Modalità Controller</h2> : <h2>Modalità Volante</h2>}
            </section>
        </>
    )
}