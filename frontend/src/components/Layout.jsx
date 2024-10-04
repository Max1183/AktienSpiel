import React from 'react';
import Navbar from '../components/Navbar'
import Footer from '../components/Footer'

function Layout({ children }) {
    return <main className="content">
        <Navbar />
        <section className="container">
            {children}
        </section>
        <Footer />
    </main>
}

export default Layout;
