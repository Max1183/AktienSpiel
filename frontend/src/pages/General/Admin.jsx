import React, { useState } from 'react';
import api from '../../api';
import { useAlert } from '../../components/Alerts/AlertProvider';
import { getError } from '../../utils/helpers';

function Admin() {
    const [email, setEmail] = useState('');
    const { addAlert } = useAlert();

    const handleSubmit = (e) => {
        e.preventDefault();
        api.post('/api/register/', {
            email: email,
        }).then(() => {
            addAlert(`Eine Aktivierungs E-Mail wurde an ${email} gesendet.`, 'success');
        }).catch((error) => {
            addAlert(getError(error), "danger")
        });
    }

    return <div className="bg-primary-subtle p-3 shadow rounded p-3">
        <h1>Admin</h1>
        <form className="row g-3" onSubmit={handleSubmit}>
             <div className="form-group col-12">
                 <input
                    type="text"
                    id="enter_email"
                    name="enter_email"
                    placeholder="Gib die E-Mail des neuen Spielers ein!"
                    value={email}
                    onChange={e => setEmail(e.target.value)}
                    className="form-control"
                />
            </div>
            <div className="form-group col-12">
                <button type="submit" className="btn btn-primary">Spieler hinzufügen</button>
            </div>
        </form>
    </div>
}

export default Admin
