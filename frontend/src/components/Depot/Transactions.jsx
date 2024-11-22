import React, { useState, useEffect } from 'react';
import api from '../../api';
import LoadingSite from '../Loading/LoadingSite';
import TransactionItem from './TransactionItem';
import { useAlert } from '../Alerts/AlertProvider';
import { getRequest } from '../../utils/helpers';

function Transactions({ team }) {
    const [transactions, setTransactions] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        getRequest('/api/transactions/', setIsLoading)
            .then(data => setTransactions(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, []);

    if (isLoading) return <LoadingSite />;

    if (!transactions) return <h2>Fehler beim Laden der Aufträge</h2>;

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
