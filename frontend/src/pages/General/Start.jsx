import React from 'react';
import Area from '../../components/General/Area';
import Navigation from '../../components/Navigation/Navigation';

function Start() {
    return <>
        <Area title="Herzlich Willkommen beim Aktienspiel 2024!">
            <p>Ihr habt die Möglichkeit den echten Börsenhandel kennenzulernen - kostenlos, realitätsnah und ganz ohne Risiko.</p>
            <p>Dabei startet ihr mit einem virtuellen Startkapital von 100.000 € und könnt damit echte Aktien kaufen und verkaufen. Wenn ihr euch gut vorbereitet habt, könnt ihr sogar einen Gewinn erzielen.</p>
            <p>Viel Erfolg und Spaß beim Handeln!</p>
            <Navigation to="/depot" name="Zum Depot" />
        </Area>
        <Area title="Schwarzes Brett" size='6'>
            <p>Das Spiel hat begonnen!</p>
        </Area>
        <Area title="Kontakt" size='6'>
            <p>Für Fragen und Anregungen könnt ihr uns gerne kontaktieren:</p>
            <p>E-Mail: <a href="mailto:info@aktienspiel.de">info@aktienspiel.de</a></p>
        </Area>
    </>
}

export default Start
