import { Link } from "react-router-dom";

function NotFound() {
    return (
        <div className="mt-5 text-center">
            <h1>Hoppla, diese Seite existiert nicht!</h1>
            <p>
                Vielleicht wurde sie verschoben oder gelöscht.
                <br />
                Bei Fragen oder Problemen, kannst du dich gerne an den Support
                wenden.
            </p>
            <p>
                Zurück zur <Link to="/">Startseite</Link>
            </p>
        </div>
    );
}

export default NotFound;
