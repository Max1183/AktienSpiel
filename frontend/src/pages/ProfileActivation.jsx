import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api';
import FormField from '../components/FormField';

function ProfileActivation({ match }) {
    const [step, setStep] = useState(0);
    const [error, setError] = useState(null);

    const { token } = useParams();
    const [isValid, setIsValid] = useState(true);

    const [email, setEmail] = useState('');
    const [joinTeam, setJoinTeam] = useState(true);
    const [joinTeamName, setJoinTeamName] = useState('');

    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        username: '',
        password: '',
        password_confirmation: '',
        team_name: '',
        team_code: ''
    });
    const [validationErrors, setValidationErrors] = useState({});

    const navigate = useNavigate();

    useEffect(() => {
        localStorage.clear();
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

    const validateField = async (fieldName, value) => {
        fieldName = fieldName === 'password_confirmation' ? 'password' : fieldName;

        if (validationErrors[fieldName] !== null) return;

        setValidationErrors({ ...validationErrors, [fieldName]: "Überprüfen..." });

        try {
            const response = await api.post('/api/validate-form/', {
                field: fieldName,
                value: value,
            });

            if (response.data.valid) {
                setValidationErrors({ ...validationErrors, [fieldName]: null });

                if (fieldName === 'team_code') {
                    setJoinTeamName(response.data.team_name);
                }
            } else {
                setValidationErrors({ ...validationErrors, [fieldName]: response.data.message });
            }
        } catch (error) {
            setError(error.message);
            try {
                setValidationErrors({ ...validationErrors, [fieldName]: error.response.data.message });
            } catch (error1) {
                setError(error.message);
            }
        }
    };

    const validateFrontend = (fieldName, value) => {
        let error = null;

        switch (fieldName) {
            case 'first_name':
                if (value.length < 3 || value.length > 20) {
                    error = "Vorname muss zwischen 3 und 20 Zeichen lang sein.";
                }
                break;
            case 'last_name':
                if (value.length < 3 || value.length > 20) {
                    error = "Nachname muss zwischen 3 und 20 Zeichen lang sein.";
                }
                break;
            case 'username':
                if (value.length < 3 || value.length > 20) {
                    error = "Benutzername muss zwischen 3 und 20 Zeichen lang sein.";
                }
                break;
            case 'password':
            case 'password_confirmation':
                const other_value = fieldName === 'password' ? formData.password_confirmation : formData.password;
                if (value.length < 8 || value.length > 20) {
                    error = "Passwort muss zwischen 8 und 20 Zeichen lang sein.";
                } else if (value !== other_value) {
                    error = "Passwort und Passwortbestätigung stimmen nicht überein.";
                }
                fieldName = 'password'
                break;
            case 'team_name':
                if (value.length < 3 || value.length > 20) {
                    error = "Teamname muss zwischen 3 und 20 Zeichen lang sein.";
                }
                break;
            case 'team_code':
                if (value.length !== 8) {
                    error = "Teamcode muss 8 Zeichen lang sein.";
                }
                break;
        }

        return [fieldName, error];
    }

    const handleChange = (e) => {
        const fieldName = e.target.name;
        const value = e.target.value;

        setFormData({ ...formData, [fieldName]: value });

        const [fieldName1, error] = validateFrontend(fieldName, value);
        setValidationErrors({ ...validationErrors, [fieldName1]: error });
    };

    const handleBlur = async (e) => {
        validateField(e.target.name, e.target.value);
    }

    const isInvalidForm = () => {
        switch (step) {
            case 0:
                return !isValid || error;
            case 1:
                return error || validationErrors['first_name'] || validationErrors['last_name'] || validationErrors['username'] || validationErrors['password'] || validationErrors['password_confirmation'];
            case 2:
                return error || (joinTeam && validationErrors['team_code']) || (!joinTeam && validationErrors['team_name']);
            case 3:
                return error;
            default:
                return true;
        }
    };

    const handleNext = () => {
        setStep(step + 1);
        setError(null);

        let newValidationErrors = {};
        Object.entries(formData).forEach(([field_name, value]) => {
            const [fieldName1, error1] = validateFrontend(field_name, value);
            newValidationErrors[fieldName1] = error1;
        });

        setValidationErrors(newValidationErrors);
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

            navigate('/login');
        } catch (err) {
            try {
                setError(err.response.data.detail)
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
                    <button type="button" className="btn btn-primary" onClick={handleNext} disabled={isInvalidForm()}>Weiter</button>
                </div>
            case 1:
                return <>
                    <FormField label="Vorname" type="text" name="first_name" value={formData.first_name}
                        onChange={handleChange} error={validationErrors.first_name} width="col-md-6" />
                    <FormField label="Nachname" type="text" name="last_name" value={formData.last_name}
                        onChange={handleChange} error={validationErrors.last_name} width="col-md-6" />
                    <FormField label="Benutzername" type="text" name="username" value={formData.username}
                        onChange={handleChange} onBlur={handleBlur} error={validationErrors.username} />
                    <FormField label="Passwort" type="password" name="password" value={formData.password}
                        onChange={handleChange} onBlur={handleBlur} error={validationErrors.password} width="col-md-6" />
                    <FormField label="Passwort bestätigen" type="password" name="password_confirmation" value={formData.password_confirmation}
                        onChange={handleChange} onBlur={handleBlur} error={validationErrors.password} width="col-md-6" />

                    <div className="col-12 d-flex justify-content-between">
                        <button className="btn btn-primary" onClick={handlePrevious}>Zurück</button>
                        <button className="btn btn-primary" onClick={handleNext} disabled={isInvalidForm()}>Weiter</button>
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
                    {joinTeam ? <>
                        <FormField label="Team-Code" type="text" name="team_code" value={formData.team_code}
                            onChange={handleChange} onBlur={handleBlur} error={validationErrors.team_code} />
                    </> : <>
                        <FormField label="Team-Name" type="text" name="team_name" value={formData.team_name}
                            onChange={handleChange} onBlur={handleBlur} error={validationErrors.team_name} />
                    </>}
                    <div className="col-12 d-flex justify-content-between">
                        <button className="btn btn-primary" onClick={handlePrevious}>Zurück</button>
                        <button className="btn btn-primary" onClick={handleNext} disabled={isInvalidForm()}>Weiter</button>
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
                                <strong>Team:</strong> {joinTeam ? `${joinTeamName ? `Team "${joinTeamName}" b` : 'B'}eitreten mit Code "${formData.team_code}"` : `"${formData.team_name}" erstellen`}<br />
                            </p>
                        </div>
                        <div className="col-12 d-flex justify-content-between">
                            <button className="btn btn-primary" onClick={handlePrevious}>Zurück</button>
                            <button className="btn btn-primary" onClick={handleSubmit} disabled={isInvalidForm()}>Bestätigen</button>
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
