import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api';

function ProfileActivation({ match }) {
    const [step, setStep] = useState(0);
    const [formData, setFormData] = useState({ first_name: '', last_name: '', username: '', password: '', password_confirmation: '', team_name: '', team_code: ''});
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
            const createUserResponse = await api.post('/api/create-user/', {
                token: token,
                email: email,
                first_name: formData.first_name,
                last_name: formData.last_name,
                username: formData.username,
                password: formData.password,
                team_code: formData.team_code,
                team_name: formData.team_name,
                join_team: joinTeam
            });

            console.log('createUserResponse:', createUserResponse);

            navigate('/login');
        } catch (err) {
            try {
                setError(err.response.data.detail[0])
            } catch (exception) {
                setError(err.message || 'Fehler beim Erstellen des Accounts.');
            }
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
                        <label htmlFor="inputFirstName" className="form-label">Vorname</label>
                        <input type="text" name="first_name" onChange={handleChange} value={formData.first_name} className="form-control" id="inputFirstName" />
                    </div>
                    <div className="col-md-6">
                        <label htmlFor="inputLastName" className="form-label">Nachname</label>
                        <input type="text" name="last_name" onChange={handleChange} value={formData.last_name} className="form-control" id="inputLastName" />
                    </div>
                    <div className="col-12">
                        <label htmlFor="inputUsername" className="form-label">Benutzername</label>
                        <input type="text" name="username" onChange={handleChange} value={formData.nickname} className="form-control" id="inputUsername" />
                    </div>
                    <div className="col-md-6">
                        <label htmlFor="inputPassword" className="form-label">Passwort</label>
                        <input type="password" name="password" onChange={handleChange} value={formData.password} className="form-control" id="inputPassword" />
                    </div>
                    <div className="col-md-6">
                        <label htmlFor="inputPasswordConfirmation" className="form-label">Passwort nochmal eingeben</label>
                        <input type="password" name="password_confirmation" onChange={handleChange} value={formData.password_confirmation} className="form-control" id="inputPasswordConfirmation" />
                    </div>
                    <div className="col-12 d-flex justify-content-between">
                        <button className="btn btn-primary" onClick={handlePrevious}>Zurück</button>
                        <button className="btn btn-primary" onClick={handleNext} disabled={!formData.first_name || !formData.last_name || !formData.username || !formData.password || !formData.password_confirmation || formData.password !== formData.password_confirmation || error}>Weiter</button>
                    </div>
                </>
            case 2:
                return <>
                    <div className="col-12 d-flex">
                        <div className="form-check">
                            <input className="form-check-input" type="radio" name="flexRadioDefault" id="flexRadioDefault1" onChange={() => setJoinTeam(true)} checked={joinTeam} />
                            <label className="form-check-label" htmlFor="flexRadioDefault1">
                                Team beitreten
                            </label>
                        </div>
                        <div className="form-check ms-5">
                            <input className="form-check-input" type="radio" name="flexRadioDefault" id="flexRadioDefault2" onChange={() => setJoinTeam(false)} checked={!joinTeam} />
                            <label className="form-check-label" htmlFor="flexRadioDefault2">
                                Team erstellen
                            </label>
                        </div>
                    </div>
                    <div className="col-12">
                        {joinTeam ? <>
                            <label htmlFor="inputTeamCode" className="form-label">Gib den Team-Code ein:</label>
                            <input type="text" name="team_code" onChange={handleChange} value={formData.team_code} className="form-control" id="inputTeamCode" />
                        </> : <>
                            <label htmlFor="inputTeamName" className="form-label">Gib den Team-Namen ein:</label>
                            <input type="text" name="team_name" onChange={handleChange} value={formData.team_name} className="form-control" id="inputTeamName" />
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
                                <strong>Benutzername:</strong> {formData.username}<br />
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
        {isValid && step > 0 && <>
            <h1>Profil aktivieren</h1>
            <p>Schritt {step} von 3</p>
            {error && <div className="alert alert-danger">{error}</div>}
        </>}
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
