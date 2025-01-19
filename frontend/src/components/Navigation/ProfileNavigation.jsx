import React from 'react';
import Navigation from './Navigation';
import { FilePerson, FilePersonFill, People, PeopleFill } from 'react-bootstrap-icons';

const ProfileNavigation = () => {
    return (
        <div className="btn-group w-100 mb-3">
            <Navigation to="/user/profile" name="Profil" icon={<FilePerson />} icon_active={<FilePersonFill />} />
            <Navigation to="/user/team" name="Team" icon={<People />} icon_active={<PeopleFill />} />
        </div>
    );
};

export default ProfileNavigation;
