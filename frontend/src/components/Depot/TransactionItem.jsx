import React, { useState } from "react";
import api from "../../api";
import { formatDate, formatCurrency } from "../../utils/helpers";
import { useAlert } from "../../components/Alerts/AlertProvider";
import StockDetailLink from "./StockDetailLink";

function TransactionItem({ transaction }) {
    const [newDescription, setNewDescription] = useState(
        transaction.description
    );
    const [showModal, setShowModal] = useState(false);
    const { addAlert } = useAlert();

    const handleClose = () => setShowModal(false);
    const handleShow = (e) => {
        e.stopPropagation();
        setShowModal(true);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (newDescription !== transaction.description) {
            try {
                const res = await api.patch(
                    `/api/transactions/${transaction.id}/update/`,
                    {
                        description: newDescription,
                    }
                );
                if (
                    res.status === 200 ||
                    res.status === 201 ||
                    res.status === 204
                ) {
                    addAlert(
                        `Beschreibung der Aktie erfolgreich geändert!`,
                        "success"
                    );
                } else {
                    addAlert("Fehler beim Ändern der Beschreibung.", "danger");
                }
            } catch (err) {
                addAlert(err.message, "danger");
            }
        }
        handleClose();
    };

    return (
        <>
            <StockDetailLink stock_id={transaction.stock.id}>
                <div className="d-flex w-100 justify-content-between">
                    <h5 className="mb-1">{transaction.stock.name}</h5>
                    <small className="text-muted">
                        {formatDate(transaction.date)}
                    </small>
                </div>
                <div className="d-flex w-100 justify-content-between">
                    <div>
                        <p className="mb-1">
                            Transaktionstyp: {transaction.transaction_type}
                        </p>
                        <p className="text-muted mb-0">
                            Anzahl: {transaction.amount}
                        </p>
                    </div>
                    <a className="btn btn-primary mt-auto" onClick={handleShow}>
                        <small>Details</small>
                    </a>
                </div>
            </StockDetailLink>

            {showModal && (
                <>
                    <div
                        className="modal fade show"
                        id={transaction.id}
                        tabIndex="-1"
                        aria-labelledby="exampleModalLabel"
                        aria-hidden="true"
                        style={{ display: "block" }}
                    >
                        <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                            <div className="modal-content">
                                <div className="modal-header">
                                    <h5 className="modal-title">
                                        {transaction.stock.name}
                                    </h5>
                                    <button
                                        type="button"
                                        className="btn-close"
                                        aria-label="Close"
                                        onClick={handleClose}
                                    ></button>
                                </div>
                                <div className="modal-body">
                                    <p>
                                        Transaktionstyp:{" "}
                                        {transaction.transaction_type}
                                        <br />
                                        Status: {transaction.status}
                                        <br />
                                        Anzahl: {transaction.amount}
                                        <br />
                                        Preis:{" "}
                                        {formatCurrency(transaction.price)}
                                        <br />
                                        Aktienwert:{" "}
                                        {formatCurrency(
                                            transaction.amount *
                                                transaction.price
                                        )}
                                        <br />
                                        Gebühren:{" "}
                                        {formatCurrency(transaction.fee)}
                                        <br />
                                        Gesamtpreis:{" "}
                                        {formatCurrency(
                                            transaction.total_price
                                        )}
                                        <br />
                                        Datum: {formatDate(transaction.date)}
                                        <br />
                                    </p>
                                    <div className="mb-3">
                                        <label
                                            htmlFor="exampleFormControlTextarea1"
                                            className="form-label"
                                        >
                                            Notiz:
                                        </label>
                                        <textarea
                                            className="form-control"
                                            id="exampleFormControlTextarea1"
                                            rows="4"
                                            value={newDescription}
                                            onChange={(e) =>
                                                setNewDescription(
                                                    e.target.value
                                                )
                                            }
                                            maxLength="1000"
                                            placeholder="Hier kannst du eine Notiz zu dieser Transaktion hinzufügen."
                                        />
                                    </div>
                                </div>
                                <div className="modal-footer">
                                    <button
                                        type="button"
                                        className="btn btn-secondary"
                                        onClick={handleClose}
                                    >
                                        Schließen
                                    </button>
                                    <button
                                        type="button"
                                        className="btn btn-primary"
                                        onClick={handleSubmit}
                                    >
                                        Speichern
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="modal-backdrop fade show"></div>
                </>
            )}
        </>
    );
}

export default TransactionItem;
