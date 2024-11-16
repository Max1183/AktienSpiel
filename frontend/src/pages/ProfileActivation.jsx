import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api';

function ProfileActivation({ match }) {
    const [step, setStep] = useState(0);
    const [formData, setFormData] = useState({ first_name: '', last_name: '', nickname: '', password: '', password_confirmation: '', team_name: '', team_code: ''});
    const [email, setEmail] = useState('');
    const [joinTeam, setJoinTeam] = useState(true);
    const [error, setError] = useState(null);
    const { token } = useParams();
    const [isValid, setIsValid] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(`/validate_activation_token/${token}/`);
                if (response.data.valid) {
                    setEmail(response.data.email);
                } else {
                    setIsValid(false);
                    setError(response.data.message);
                }
            } catch (error) {
                setError(error.message);
            }
        };
        fetchData();
    }, [token]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleNext = () => {
        if (step === 1 && formData.password !== formData.password_confirmation) {
            setError("Passwörter stimmen nicht überein.");
            return;
        }
        setStep(step + 1);
        setError(null);
    };

    const handlePrevious = (e) => {
        e.preventDefault();
        setStep(step - 1);
        setError(null);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const createUserResponse = await api.post('/api/create_user/', {
                token: token,
                email: email,
                first_name: formData.first_name,
                last_name: formData.last_name,
                nickname: formData.nickname,
                password: formData.password,
                team_name: formData.team_name,
                team_code: formData.team_code,
                join_team: joinTeam
            });

            localstorage.clear();
            navigate('/login');
        } catch (err) {
            setError(err.message || 'Fehler beim Erstellen des Accounts.');
            addAlert('Fehler beim Erstellen des Accounts!', 'danger');
        }
    };

    const renderStep = () => {
        switch (step) {
            case 0:
                return <div className="text-center mt-5">
                    <h1>Herzlich Willkommen beim Aktienspiel</h1>
                    <p className="fs-5">Bitte gib zuerst ein paar Informationen an, dann kann es losgehen!</p>
                    <button type="button" className="btn btn-primary" onClick={handleNext} disabled={!isValid || error}>Weiter</button>
                </div>
            case 1:
                return <>
                    <div className="col-md-6">
                        <label for="inputFirstName" class="form-label">Vorname</label>
                        <input type="text" name="first_name" onChange={handleChange} value={formData.first_name} class="form-control" id="inputFirstName" />
                    </div>
                    <div className="col-md-6">
                        <label for="inputLastName" class="form-label">Nachname</label>
                        <input type="text" name="last_name" onChange={handleChange} value={formData.last_name} class="form-control" id="inputLastName" />
                    </div>
                    <div className="col-12">
                        <label for="inputNickname" class="form-label">Spitzname</label>
                        <input type="text" name="nickname" onChange={handleChange} value={formData.nickname} class="form-control" id="inputNickname" />
                    </div>
                    <div className="col-md-6">
                        <label for="inputPassword" class="form-label">Passwort</label>
                        <input type="password" name="password" onChange={handleChange} value={formData.password} class="form-control" id="inputPassword" />
                    </div>
                    <div className="col-md-6">
                        <label for="inputPasswordConfirmation" class="form-label">Passwort nochmal eingeben</label>
                        <input type="password" name="password_confirmation" onChange={handleChange} value={formData.password_confirmation} class="form-control" id="inputPasswordConfirmation" />
                    </div>
                    <div className="col-12 d-flex justify-content-between">
                        <button className="btn btn-primary" onClick={handlePrevious}>Zurück</button>
                        <button className="btn btn-primary" onClick={handleNext} disabled={!formData.first_name || !formData.last_name || !formData.nickname || !formData.password || !formData.password_confirmation || formData.password !== formData.password_confirmation || error}>Weiter</button>
                    </div>
                </>
            case 2:
                return <>
                    <div className="col-12 d-flex">
                        <div className="form-check">
                            <input className="form-check-input" type="radio" name="flexRadioDefault" id="flexRadioDefault1" onChange={() => setJoinTeam(true)} checked={joinTeam} />
                            <label className="form-check-label" for="flexRadioDefault1">
                                Team beitreten
                            </label>
                        </div>
                        <div className="form-check ms-5">
                            <input className="form-check-input" type="radio" name="flexRadioDefault" id="flexRadioDefault2" onChange={() => setJoinTeam(false)} checked={!joinTeam} />
                            <label className="form-check-label" for="flexRadioDefault2">
                                Team erstellen
                            </label>
                        </div>
                    </div>
                    <div className="col-12">
                        {joinTeam ? <>
                            <label for="inputTeamCode" class="form-label">Gib den Team-Code ein:</label>
                            <input type="text" name="team_code" onChange={handleChange} value={formData.team_code} class="form-control" id="inputTeamCode" />
                        </> : <>
                            <label for="inputTeamName" class="form-label">Gib den Team-Namen ein:</label>
                            <input type="text" name="team_name" onChange={handleChange} value={formData.team_name} class="form-control" id="inputTeamName" />
                        </>}
                    </div>
                    <div className="col-12 d-flex justify-content-between">
                        <button className="btn btn-primary" onClick={handlePrevious}>Zurück</button>
                        <button className="btn btn-primary" onClick={handleNext} disabled={(!formData.team_code && joinTeam) || (!formData.team_name && !joinTeam) || error}>Weiter</button>
                    </div>
                </>
            case 3:
                return (
                    <div>
                        <div className="col-12">
                            <strong>Bitte überprüfe die eingegebenen Daten und klicke dann auf Bestätigen</strong>
                            <p>
                                <br />
                                <strong>Vorname:</strong> {formData.first_name}<br />
                                <strong>Nachname:</strong> {formData.last_name}<br />
                                <strong>Spitzname:</strong> {formData.nickname}<br />
                                <strong>E-Mail:</strong> {email}<br />
                                <strong>Team:</strong> {joinTeam ? `Beitreten mit Code "${formData.team_code}"` : `"${formData.team_name}" erstellen`}<br />
                            </p>
                        </div>
                        <div className="col-12 d-flex justify-content-between">
                            <button className="btn btn-primary" onClick={handlePrevious}>Zurück</button>
                            <button className="btn btn-primary" onClick={handleSubmit} disabled={error}>Bestätigen</button>
                        </div>
                    </div>
                );
            default:
                setStep(0);
                return null;
        }
    };

    return <div className="container mt-5">
        {step > 0 && <>
            <h1>Profil aktivieren</h1>
            <p>Schritt {step} von 3</p>
        </>}
        {error && <div className="alert alert-danger">{error}</div>}
        {!isValid ? (
            <div className="text-center mt-5">
                <h1>Hoppla, dein Token leider nicht gültig</h1>
                <p className="fs-5">Vielleicht ist er abgelaufen oder du hast du ihn schon mal verwendet.</p>
                <p>Bei Fragen, wende dich gerne an unseren Support: <a href="mailto:aktienspiel01@gmail.com">aktienspiel01@gmail.com</a></p>
            </div>
        ) : (
            <form className="row g-3">
                {renderStep()}
            </form>
        )}
    </div>
}

export default ProfileActivation;
