import Layout from "../components/Layout";
import React from "react";
import { useParams } from 'react-router-dom';

function Transaction() {
    const { t } = useParams();
    const { id } = useParams();

    return <Layout>
        <h1>Order Formular</h1>
        <p>Hier können Sie Transaktionen durchführen.</p>
        <p>Transaktionstyp: {t}</p>
        <p>Aktie: {id}</p>
    </Layout>
}

export default Transaction;
