import React, { useRef, useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';

function ProfileDropdown () {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);

    const toggleDropdown = () => {
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
                href="#"
                role="button"
                aria-expanded={isOpen}
                onClick={toggleDropdown}
            >
                <img src="/Profile.png" className="profile" width="40" height="40" alt="Profile" />
            </a>
            <ul className={`dropdown-menu ${isOpen && 'show'}`}>
                <li>
                    <NavLink
                        to="/user/profile"
                        className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                        onClick={toggleDropdown}
                    >
                        Profil
                    </NavLink>
                </li>
                <li>
                    <NavLink
                        to="/user/team"
                        className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                        onClick={toggleDropdown}
                    >
                        Team
                    </NavLink>
                </li>
                <li><hr className="dropdown-divider" /></li>
                <li>
                    <NavLink
                        to="/logout"
                        className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                        onClick={toggleDropdown}
                    >
                        Logout
                    </NavLink>
                </li>
            </ul>
        </li>
    </ul>
}

export default ProfileDropdown;
