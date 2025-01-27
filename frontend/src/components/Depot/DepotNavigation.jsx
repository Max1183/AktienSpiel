import { NavLink, useLocation } from 'react-router-dom';
import { useWindowSize } from '../../App.jsx';

function DepotNavigation({ to, name, icon, icon_active }) {
    const { width } = useWindowSize();
    const small = width < 500;
    const location = useLocation();

    const isActive = () => {
        return location.pathname === to || location.pathname === to + "/";
    };

    const getClassName = () => {
        return `btn btn-primary ${isActive() && 'active'}`;
    };

    const getName = () => {
        return small ? (isActive() ? icon_active : icon) : name;
    };

    return <>
        <NavLink to={to} end className={getClassName()}>
            {getName()}
        </NavLink>
    </>;
}

export default DepotNavigation;
