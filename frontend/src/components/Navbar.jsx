import { NavLink } from 'react-router-dom';
import SearchBar from './SearchBar'
import "../styles/Navbar.css";

function Navbar ({ small }) {
    const navbar_small = (
        <nav className="navbar bg-dark navbar-expand-lg sticky-top" data-bs-theme="dark">
            <div className="container-fluid">
                <button className="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar" aria-controls="offcanvasNavbar" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <a className="navbar-brand mb-0 h1" href="/">
                    <img src="/Logo.png" className="logo" id="logo" width="183" height="50" alt="Logo" />
                </a>
                <a className="navbar-brand mb-0 h1" href="/profile/">
                    <img src="/Profile.png" className="profile" width="40" height="40" alt="Profile" />
                </a>
                <div className="offcanvas offcanvas-start" tabIndex="-1" id="offcanvasNavbar" aria-labelledby="offcanvasNavbarLabel" data-bs-scroll="true">
                    <div className="offcanvas-header">
                        <h5 className="offcanvas-title" id="offcanvasNavbarLabel">Navigation</h5>
                        <button type="button" className="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
                    </div>
                    <div className="offcanvas-body">
                        <ul className="navbar-nav justify-content-end flex-grow-1 pe-3">
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
                                  to="/depot/"
                                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                                  aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                                >
                                  DEPOT
                                </NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink
                                    to="/contest/"
                                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                                    aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                                >
                                    WETTBEWERB
                                </NavLink>
                            </li>
                        </ul>
                        <SearchBar />
                    </div>
                </div>
            </div>
        </nav>
    )

    const navbar_big = (
        <nav className="navbar bg-dark navbar-expand-lg sticky-top" data-bs-theme="dark">
            <div className="container-fluid">
                <a className="navbar-brand me-auto mb-0 h1" href="/">
                    <img src="/Logo.png" className="logo" id="logo" width="183" height="50" alt="Logo" />
                </a>
                <ul className="navbar-nav me-auto mb-2 mb-lg-0">
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
                          to="/depot/"
                          className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                          aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                        >
                          DEPOT
                        </NavLink>
                    </li>
                    <li className="nav-item">
                        <NavLink
                          to="/contest/"
                          className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                          aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                        >
                          WETTBEWERB
                        </NavLink>
                    </li>
                </ul>
                <SearchBar />
                <a className="navbar-brand mb-0 h1" href="/profile/">
                    <img src="/Profile.png" className="profile" width="40" height="40" alt="Profile" />
                </a>
            </div>
        </nav>
    )

    return small ? navbar_small : navbar_big;
}

export default Navbar;
