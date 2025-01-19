import React, { useRef, useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import SearchBar from '../Depot/SearchBar'
import ProfileDropdown from './ProfileDropdown'
import { PersonCircle } from 'react-bootstrap-icons';

function Navbar ({ small }) {
    const navbar_small = (
        <nav className="navbar bg-dark navbar-expand-lg sticky-top" data-bs-theme="dark">
            <div className="container-fluid">
                <button className="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar" aria-controls="offcanvasNavbar" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                </button>
                <a className="navbar-brand mb-0 d-flex align-items-center" href="/">
                    <img src="/Logo.png" className="mx-3" id="logo" alt="Logo" />
                    <p className="m-0 fs-4">Aktienspiel</p>
                </a>
                <a className="navbar-brand mb-0 h1" href="/user/profile/">
                    <PersonCircle width="40" height="40" alt="Profile" />
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
                                    to="/user/profile"
                                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                                    aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                                >
                                    PROFIL
                                </NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink
                                    to="/user/team"
                                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                                    aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                                >
                                    TEAM
                                </NavLink>
                            </li>
                            <li className="nav-item">
                                <NavLink
                                    to="/logout"
                                    className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                                    aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                                >
                                    LOGOUT
                                </NavLink>
                            </li>
                        </ul>
                        <div className="mt-3">
                            <SearchBar />
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    )

    const navbar_big = (
        <nav className="navbar bg-dark navbar-expand-lg sticky-top" data-bs-theme="dark">
            <div className="container-fluid">
                <a className="navbar-brand me-auto mb-0 d-flex align-items-center" href="/">
                    <img src="/Logo.png" className="ms-5 me-3" id="logo" alt="Logo" />
                    <p className="m-0 fs-3">Aktienspiel</p>
                </a>
                <ul className="navbar-nav mb-2 mb-lg-0">
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
                </ul>
                <ProfileDropdown />
                <SearchBar />
            </div>
        </nav>
    )

    return small ? navbar_small : navbar_big;
}

export default Navbar;
