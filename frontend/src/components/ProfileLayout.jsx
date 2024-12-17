import { useNavigate, NavLink } from 'react-router-dom';

function ProfileLayout({ children }) {
    const navigate = useNavigate();

    const handleNavigation = (path) => {
        navigate(path);
    };

    const getClassName = (isActive) => {
        return `btn btn-primary ${isActive && 'active'}`;
    };

    return <>
        <div className="btn-group w-100 mb-3">
            <NavLink to="/user/profile" className={({ isActive }) => getClassName(isActive)}>Profil</NavLink>
            <NavLink to="/user/team" className={({ isActive }) => getClassName(isActive)}>Team</NavLink>
        </div>
        {children}
    </>
}

export default ProfileLayout
