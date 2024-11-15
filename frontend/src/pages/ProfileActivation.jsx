import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom'
import api from '../api';
import { useAlert } from '../components/Alerts/AlertProvider';

function ProfileActivation({ match }) {
    const [formData, setFormData] = useState({ first_name: '', last_name: '', nickname: '', password: '' });
    const [email, setEmail] = useState('');
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const token = useParams()
    const { addAlert } = useAlert();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await api.get(`/validate_activation_token/${token}/`);
                if (response.data.valid) {
                    setEmail(response.data.email);
                } else {
                    setError(response.data.message);
                    addAlert('Aktivierung fehlgeschlagen!', 'danger');
                }
            } catch (error) {
                setError(error.message);
                addAlert('Aktivierung fehlgeschlagen!', 'danger');
            }
        };
        fetchData();
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const createUserResponse = await axios.post('/api/create_user/', {
                token: token,
                email: email,
                first_name: formData.first_name,
                last_name: formData.last_name,
                nickname: formData.nickname,
                password: formData.password,
            });

            addAlert('Account erfolgreich erstellt!');
        } catch (err) {
            setError(err.message || 'Fehler beim Erstellen des Accounts.');
            addAlert('Fehler beim Erstellen des Accounts!', 'danger');
        }
    };

    return (
        <div>
            {/* ... Formular und Fehler/Erfolgsmeldungen ... */}
        </div>
    )
}

export default ProfileActivation;
