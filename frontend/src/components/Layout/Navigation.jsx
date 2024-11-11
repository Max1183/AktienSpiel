import { NavLink } from 'react-router-dom';
import "../../styles/Navbar.css";

function Navigation () {
    return <nav className="navbar bg-dark navbar-expand-lg sticky-bottom" data-bs-theme="dark">
        <div className="container-fluid">
            <ul className="navbar-nav d-flex flex-row gap-3 mb-lg-0">
                <li className="nav-item">
                    <NavLink
                      to="/"
                      className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                      aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                      end
                    >
                      START
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink
                      to="/depot"
                      className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                      aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                    >
                      DEPOT
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink
                      to="/contest"
                      className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                      aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                    >
                      WETTBEWERB
                    </NavLink>
                </li>
                <li className="nav-item">
                    <NavLink
                      to="/depot/search/"
                      className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                      aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                    >
                      <img src="/SearchIcon.png" alt="Search" width="27" height="20" className="d-inline-block align-text-top" />
                    </NavLink>
                </li>
            </ul>
        </div>
    </nav>
}

export default Navigation;
