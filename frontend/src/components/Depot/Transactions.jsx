import React from 'react';
import TransactionItem from './TransactionItem';
import { useOutletContext } from 'react-router-dom';
import DepotArea from './DepotArea';

function Transactions({ team }) {
    const { transactions, loadTransactions } = useOutletContext();

    return <>
        <DepotArea title="Meine Transaktionen" value={transactions} handleReload={loadTransactions} size="12">
            {transactions && <>
                <p>Durch Klicken auf die Transaktionen gelangst du zu den Aktien.</p>
                <div className="list-group rounded mt-3">
                    {transactions.map((transaction) => (
                        <TransactionItem transaction={transaction} key={transaction.id} />
                    ))}
                </div>
            </>}
        </DepotArea>
    </>
}

export default Transactions;
