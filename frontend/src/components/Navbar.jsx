import React, { useState, useRef, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import "../styles/Navbar.css";

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

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

  return (
    <>
      <nav className={`navbar navbar-expand-lg ${isScrolled ? 'navbar-dark' : ''} shadow-5-strong fixed-top navbar-scroll ${isScrolled && 'scrolled'}`}>
        <div className="container-fluid">
          <a className="navbar-brand mb-0 h1" href="/">
            <img src="/Logo.png" class={`logo ${isScrolled && 'scrolled'}`} id="logo" width="183" height="50" alt="Logo" />
          </a>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              <li className="nav-item">
                <NavLink
                  to="/"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                  aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                  end
                >
                  HOME
                </NavLink>
              </li>
              <li className="nav-item">
                <NavLink
                  to="/about/"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                  aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                >
                  ABOUT
                </NavLink>
              </li>
              <li className="nav-item dropdown" ref={dropdownRef}>
                <a
                  className={`nav-link dropdown-toggle ${isOpen ? 'show' : ''}`}
                  href="#"
                  role="button"
                  data-bs-toggle="dropdown"
                  aria-expanded={isOpen}
                  onClick={(e) => {e.preventDefault(); toggleDropdown();}}
                >
                  STATISTICS
                </a>
                <ul className={`dropdown-menu ${isOpen ? 'show' : ''}`}>
                  <li>
                    <NavLink
                      to="/statistics/create/"
                      className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                      onClick={toggleDropdown}
                    >
                      Create statistics
                    </NavLink>
                  </li>
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <NavLink
                      to="/statistics/create/excel"
                      className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                      onClick={toggleDropdown}
                    >
                      Upload excel
                    </NavLink>
                  </li>
                  <li>
                    <NavLink
                      to="/statistics/create/json/"
                      className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                      onClick={toggleDropdown}
                    >
                      Upload json
                    </NavLink>
                  </li>
                  <li>
                    <NavLink
                      to="/statistics/create/manual"
                      className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                      onClick={toggleDropdown}
                    >
                      Create manually
                    </NavLink>
                  </li>
                  <li><hr className="dropdown-divider" /></li>
                  <li>
                    <NavLink
                      to="/statistics/view"
                      className={({ isActive }) => `dropdown-item ${isActive ? 'active' : ''}`}
                      onClick={toggleDropdown}
                    >
                      View statistics
                    </NavLink>
                  </li>
                </ul>
              </li>
              <li className="nav-item">
                <NavLink
                  to="/contact/"
                  className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
                  aria-current={({ isActive }) => (isActive ? "page" : undefined)}
                >
                  CONTACT
                </NavLink>
              </li>
            </ul>
            <form className="d-flex" role="search">
              <input className="form-control me-2" type="search" placeholder="Search" aria-label="Search" />
              <button className="btn btn-outline-success" type="submit">Search</button>
            </form>
          </div>
        </div>
      </nav>
      <div className="navbar-background"></div>
    </>
  );
}

export default Navbar;
