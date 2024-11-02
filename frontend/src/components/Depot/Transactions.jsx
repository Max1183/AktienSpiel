import React from 'react';
import { useState, useEffect } from 'react'
import api from '../../api';
import LoadingSite from '../Loading/LoadingSite';
import TransactionItem from './TransactionItem';

function Transactions({ team }) {
    const [transactions, setTransactions] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const [err, setErr] = useState(null);

    useEffect(() => {
        const getTransactions = async () => {
            try {
                const response = await api.get(`/api/transactions/`);
                const sortedTransactions = [...response.data].sort((a, b) => new Date(b.date) - new Date(a.date));
                setTransactions(sortedTransactions);
                setErr(null);
            } catch (error) {
                setErr(error.message);
            } finally {
                setIsLoading(false);
            }
        };

        getTransactions();
    }, []);

    if (isLoading) {
        return <LoadingSite withLayout={false} />;
    }

    if (!transactions) {
        console.log(err);
        return <>
            <h2>Fehler beim Laden der Aufträge</h2>
            {err && <p>Nachricht: {err}</p>}
        </>
    }

    return <div className="bg-primary-subtle p-3 shadow rounded p-3">
        <h2 className="mb-0">Meine Transaktionen</h2>
        <small>Durch Klicken auf die Transaktionen gelangst du zu den Aktien.</small>
        <div className="list-group rounded mt-3">
            {transactions.map((transaction) => (
                <TransactionItem transaction={transaction} key={transaction.id} />
            ))}
        </div>
    </div>
}

export default Transactions;
