import '../style.css'

export default function ClientPanel({selector}) {

    return (
        <>
            <section>
                {selector ?
                <>
                    <h2>Modalità Controller</h2>
                    <div id="controller"></div>
                </>
                 : 
                 <>
                    <h2>Modalità Volante</h2>
                    <div id="volante"></div>
                 </>
                }   
            </section>
        </>
    )
}