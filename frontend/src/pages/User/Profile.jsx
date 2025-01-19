import React from 'react';
import ProfileNavigation from '../../components/Navigation/ProfileNavigation';
import Area from '../../components/General/Area';
import { useOutletContext } from 'react-router-dom';

function Profile() {
    const { getData } = useOutletContext();

    return <>
        <ProfileNavigation />
        <Area title="Profil" key1="profile">
            {getData("profile") && <>
                <p className="fs-5 mt-3">
                    Nutzername: {getData("profile").user.username}<br />
                    Teamname: {getData("profile").team}<br />
                    Vorname: {getData("profile").user.first_name}<br />
                    Nachname: {getData("profile").user.last_name}<br />
                    E-Mail: {getData("profile").user.email}<br />
                </p>
                <a href="/logout" className="btn btn-primary">Logout</a>
            </>}
        </Area>
    </>
}

export default Profile
