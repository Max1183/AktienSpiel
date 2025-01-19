import {useState} from 'react'
import api from '../../api'
import { useNavigate } from 'react-router-dom'
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../constants'
import "../../styles/Form.css"
import LoadingIndicator from '../../components/Loading/LoadingIndicator'

function Login() {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        setLoading(true)
        e.preventDefault()

        try {
            setError(null);
            const response = await api.post("/api/token/", {username, password});
            localStorage.setItem(ACCESS_TOKEN, response.data.access)
            localStorage.setItem(REFRESH_TOKEN, response.data.refresh)
            navigate('/')
        } catch (error) {
            try {
                if (error.response.status === 401) {
                    setError("Benutzername oder Passwort falsch!")
                } else {
                    console.error(error);
                    setError(error.message);
                }
            } catch (e) {
                setError(error.message);
            }
        } finally {
            setLoading(false)
        }
    }

    return <div className="container">
        <form onSubmit={handleSubmit} className="form-container">
            <h1>Anmelden</h1>
            <input
                className="form-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Benutzername"
            />
            <input
                className="form-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Passwort"
            />
            {loading && <LoadingIndicator />}
            {error && <p className="text-danger">{error}</p>}
            <button className="form-button" type="submit">Anmelden</button>
        </form>
    </div>
}

export default Login
