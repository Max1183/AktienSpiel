import React from 'react';
import TransactionItem from './TransactionItem';
import { useOutletContext } from 'react-router-dom';
import DepotArea from './DepotArea';

function Transactions() {
    const { getData } = useOutletContext();

    return <>
        <DepotArea title="Meine Transaktionen" key1="transactions" size="12">
           {getData("transactions") && (
                <>
                    <p>Durch Klicken auf die Transaktionen gelangst du zu den Aktien.</p>
                    <div className="list-group rounded mt-3">
                        {getData("transactions").map((transaction) => (
                            <TransactionItem transaction={transaction} key={transaction.id} />
                        ))}
                    </div>
                </>
            )}
        </DepotArea>
    </>
}

export default Transactions;
