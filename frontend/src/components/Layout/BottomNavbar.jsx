import { NavLink } from 'react-router-dom';
import { Search } from 'react-bootstrap-icons';

function BottomNavbar () {
    return <nav className="navbar bg-dark navbar-expand-lg sticky-bottom" data-bs-theme="dark">
        <div className="container-fluid">
            <ul className="navbar-nav d-flex flex-row gap-4 me-auto mb-lg-0 fs-5">
                <li className="nav-item">
                    <NavLink
                        to="/"
                        className={({ isActive }) => `nav-link ${isActive && 'active'}`}
                        aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                        end
                    >
                        START
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink
                        to="/depot"
                        className={({ isActive }) => `nav-link ${isActive && 'active'}`}
                        aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                    >
                        DEPOT
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink
                        to="/contest"
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                    >
                        WETTBEWERB
                    </NavLink>
                </li>
            </ul>
            <NavLink
              to="/depot/search"
              className="navbar-brand"
              aria-current={({ isActive }) => (isActive ? "page" : undefined)}
            >
                <Search width="25" height="25" alt="Search" />
            </NavLink>
        </div>
    </nav>
}

export default BottomNavbar;
