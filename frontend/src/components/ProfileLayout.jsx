import { useNavigate, NavLink } from 'react-router-dom';

function ProfileLayout({ children }) {
    const navigate = useNavigate();

    const handleNavigation = (path) => {
        navigate(path);
    };

    const getClassName = (isActive) => {
        return `list-group-item list-group-item-action list-group-item-primary text-center p-2 ${isActive ? 'active' : ''}`;
    };

    return <>
        <div className="list-group list-group-horizontal mb-3">
            <NavLink to="/user/profile" className={({ isActive }) => getClassName(isActive)}>Profil</NavLink>
            <NavLink to="/user/team" className={({ isActive }) => getClassName(isActive)}>Team</NavLink>
        </div>
        {children}
    </>
}

export default ProfileLayout
