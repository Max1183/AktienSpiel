import React from 'react';
import TransactionItem from '../../components/Depot/TransactionItem';
import Area from '../../components/General/Area';
import DepotNavigation from '../../components/Navigation/DepotNavigation';

function Transactions() {
    return <>
        <DepotNavigation />
        <Area title="Meine Transaktionen" key1="transactions" size="12">
        {({ value: transactions }) => transactions.length > 0 ? (
                <>
                    <p>Durch Klicken auf die Transaktionen gelangst du zu den Aktien.</p>
                    <div className="list-group rounded mt-3">
                        {transactions.map((transaction) => (
                            <TransactionItem transaction={transaction} key={transaction.id} />
                        ))}
                    </div>
                </>
            ) : (
                <p>Du hast noch keine Transaktionen durchgeführt.</p>
            )}
        </Area>
    </>
}

export default Transactions;
