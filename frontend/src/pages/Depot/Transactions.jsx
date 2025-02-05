import React from "react";
import TransactionItem from "../../components/Depot/TransactionItem";
import Area from "../../components/General/Area";
import DepotNavigation from "../../components/Navigation/DepotNavigation";

function Transactions() {
    return (
        <Area
            title="Meine Transaktionen"
            key1="transactions"
            frontendPagination={true}
            size="12"
        >
            {({ value: transactions }) =>
                transactions.length > 0 ? (
                    <>
                        <p>
                            In den Details erfährst du genaueres über die
                            Transaktionen.
                        </p>
                        <div className="list-group rounded mt-3">
                            {transactions.map((transaction) => (
                                <TransactionItem
                                    transaction={transaction}
                                    key={transaction.id}
                                />
                            ))}
                        </div>
                    </>
                ) : (
                    <p>Du hast noch keine Transaktionen durchgeführt.</p>
                )
            }
        </Area>
    );
}

export default Transactions;
