import React, { useRef, useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { PersonCircle } from 'react-bootstrap-icons';

function ProfileDropdown () {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    const toggleDropdown = (e) => {
        e.preventDefault();
        setIsOpen(!isOpen);
    };

    useEffect(() => {
        function handleClickOutside(event) {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [dropdownRef]);

    return <ul className="navbar-nav mb-0 me-auto">
        <li className="nav-item dropdown" ref={dropdownRef}>
            <a
                className={`nav-link dropdown-toggle ${isOpen && 'show'}`}
                href=""
                role="button"
                aria-expanded={isOpen}
                onClick={toggleDropdown}
            >
                <PersonCircle width="40" height="40" alt="Profile" />
            </a>
            <ul className={`dropdown-menu ${isOpen && 'show'}`}>
                <li>
                    <NavLink
                        to="/user/profile"
                        className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                        onClick={() => setIsOpen(false)}
                    >
                        Profil
                    </NavLink>
                </li>
                <li>
                    <NavLink
                        to="/user/team"
                        className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                        onClick={() => setIsOpen(false)}
                    >
                        Team
                    </NavLink>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                    <NavLink
                        to="/logout"
                        className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                        onClick={() => setIsOpen(false)}
                    >
                        Logout
                    </NavLink>
                </li>
            </ul>
        </li>
    </ul>
}

export default ProfileDropdown;
