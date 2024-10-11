import {useState} from 'react'
import Layout from '../components/Layout'

function Start() {
    return <Layout>
        <div className="row">
            <div className="col-sm-12 p-3">
                <div className="bg-primary-subtle p-3 shadow rounded">
                    <h2>Herzlich Willkommen beim Börsenspiel 2024!</h2>
                    <p>Ihr habt die Möglichkeit den echten Börsenhandel kennenzulernen - kostenlos, realitätsnah und ganz ohne Risiko.</p>
                    <p>Dabei startet ihr mit einem virtuellen Startkapital von 100.000 Euro und könnt damit echte Aktien kaufen und verkaufen. Wenn ihr euch gut vorbereitet habt, könnt ihr sogar einen Gewinn erzielen.</p>
                    <p>Viel Erfolg und Spaß beim Handeln!</p>
                    <a href="/depot/" className="btn btn-primary">Zum Depot</a>
                </div>
            </div>
            <div className="col-sm-8 p-3">
                <div className="bg-primary-subtle p-3 shadow rounded">
                    <h2>Schwarzes Brett</h2>
                    <p>Das Spiel beginnt am 01.11.2024</p>
                </div>
            </div>
            <div className="col-sm-4 p-3">
                <div className="bg-primary-subtle p-3 shadow rounded">
                    <h2>Kontakt</h2>
                    <p>Für Fragen und Anregungen könnt ihr uns gerne kontaktieren:</p>
                    <p>E-Mail: info@boerse-spiel.de</p>
                    <p>Telefon: 01234 567890</p>
                </div>
            </div>
        </div>
    </Layout>
}

export default Start
