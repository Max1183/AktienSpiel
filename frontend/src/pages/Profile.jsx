import React, { useState, useEffect } from 'react';
import ProfileLayout from '../components/ProfileLayout';
import LoadingSite from '../components/Loading/LoadingSite';
import { getRequest } from '../utils/helpers';
import { useAlert } from '../components/Alerts/AlertProvider';

function Profile() {
    const [profile, setProfile] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        getRequest('/api/profile/', setIsLoading)
            .then(data => setProfile(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, []);

    if (isLoading) return <ProfileLayout>
        <LoadingSite />
    </ProfileLayout>

    if (!profile) return <ProfileLayout>
        <h2>Fehler beim Laden des Profils!</h2>
    </ProfileLayout>

    return <ProfileLayout>
        <div className="bg-primary-subtle p-3 shadow rounded p-3">
            <h2>Mein Profil</h2>
            <p className="fs-5 mt-3">
                Mein Name: {profile.user.username}<br />
                Mein Team: {profile.team_name}<br />
                Vorname: {profile.user.first_name}<br />
                Nachname: {profile.user.last_name}<br />
                E-Mail: {profile.user.email}<br />
            </p>
            <a href="/logout" className="btn btn-primary">Logout</a>
        </div>
    </ProfileLayout>
}

export default Profile
