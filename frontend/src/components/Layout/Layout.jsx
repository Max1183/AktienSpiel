import React, { useState, useEffect } from 'react';
import Navbar from '../Layout/Navbar'
import Footer from '../Layout/Footer'
import Navigation from '../Layout/Navigation'

function useWindowSize() {
  const [windowSize, setWindowSize] = useState({
    width: undefined,
    height: undefined,
  });

  useEffect(() => {
    function handleResize() {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    }

    window.addEventListener('resize', handleResize);
    handleResize();

    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

function Layout({ children }) {
    const { width } = useWindowSize();
    const small = width < 992;
    const breakpoint = 992;

    return <main className="content">
        <Navbar small={small} />
        <section className="container mt-3">
            {children}
        </section>
        {small ? <Navigation /> : <Footer />}
    </main>
}

export default Layout;
