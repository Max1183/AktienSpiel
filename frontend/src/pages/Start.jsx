import {useState} from 'react'

function Start() {
    return <div className="row">
        <div className="col-sm-12 p-3">
            <div className="bg-primary-subtle p-3 shadow rounded">
                <h2>Herzlich Willkommen beim Aktienspiel 2024!</h2>
                <p>Ihr habt die Möglichkeit den echten Börsenhandel kennenzulernen - kostenlos, realitätsnah und ganz ohne Risiko.</p>
                <p>Dabei startet ihr mit einem virtuellen Startkapital von 100.000 € und könnt damit echte Aktien kaufen und verkaufen. Wenn ihr euch gut vorbereitet habt, könnt ihr sogar einen Gewinn erzielen.</p>
                <p>Viel Erfolg und Spaß beim Handeln!</p>
                <a href="/depot" className="btn btn-primary">Zum Depot</a>
            </div>
        </div>
        <div className="col-sm-6 p-3">
            <div className="bg-primary-subtle p-3 shadow rounded h-100">
                <h2>Schwarzes Brett</h2>
                <p>Das Spiel hat begonnen!</p>
            </div>
        </div>
        <div className="col-sm-6 p-3">
            <div className="bg-primary-subtle p-3 shadow rounded h-100">
                <h2>Kontakt</h2>
                <p>Für Fragen und Anregungen könnt ihr uns gerne kontaktieren:</p>
                <p>E-Mail: <a href="mailto:aktienspiel01@gmail.com">aktienspiel01@gmail.com</a></p>
            </div>
        </div>
    </div>
}

export default Start
