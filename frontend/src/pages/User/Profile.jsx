import React from 'react';
import ProfileNavigation from '../../components/Navigation/ProfileNavigation';
import Area from '../../components/General/Area';

function Profile() {
    return <>
        <ProfileNavigation />
        <Area title="Profil" key1="profile">
            {({ value: profile }) => <>
                <p className="fs-5 mt-3">
                    Nutzername: {profile.user.username}<br />
                    Teamname: {profile.team}<br />
                    Vorname: {profile.user.first_name}<br />
                    Nachname: {profile.user.last_name}<br />
                    E-Mail: {profile.user.email}<br />
                </p>
                <a href="/logout" className="btn btn-primary">Logout</a>
            </>}
        </Area>
    </>
}

export default Profile
