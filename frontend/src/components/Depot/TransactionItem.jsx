import React, { useState } from 'react';
import api from '../../api';
import { Offcanvas, Form, Button } from 'react-bootstrap';
import 'bootstrap/dist/js/bootstrap.bundle.min'; // Importiere Bootstrap JavaScript

function formatDate(dateString) {
    const date = new Date(dateString);

    const optionsDate = { year: 'numeric', month: '2-digit', day: '2-digit' };
    const optionsTime = { hour: '2-digit', minute: '2-digit' };

    const formattedDate = date.toLocaleDateString('de-DE', optionsDate);
    const formattedTime = date.toLocaleTimeString('de-DE', optionsTime);

    return `${formattedDate} ${formattedTime}`;
}

function TransactionItem({ transaction }) {
    const [newDescription, setNewDescription] = useState(transaction.description);
    const [showModal, setShowModal] = useState(false);

    const handleClose = () => setShowModal(false);
    const handleShow = (e) => {
        e.preventDefault();
        setShowModal(true);
    }

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (newDescription !== transaction.description) {
            try {
                const res = await api.patch(`/api/transactions/${transaction.id}/`, {
                    description: newDescription
                });
                if (res.status === 200 || res.status === 201) {
                    console.log(`Beschreibung der Aktie erfolgreich geändert!`);
                } else if (res.status === 204) {
                    console.log('No content');
                } else {
                    alert('Fehler beim Ändern der Beschreibung.');
                }
            } catch (err) {
                alert(err);
            }
        }
        handleClose();
    };

    return (
        <>
            <a className="list-group-item list-group-item-action" key={transaction.id} href={`stocks/${transaction.stock.id}`}>
                <div className="d-flex w-100 justify-content-between">
                    <h5 className="mb-1">{transaction.stock.name}</h5>
                    <small className="text-muted">{formatDate(transaction.date)}</small>
                </div>
                <div className="d-flex w-100 justify-content-between">
                    <div>
                        <p className="mb-1">Transaktionstyp: {transaction.transaction_type}</p>
                        <p className="text-muted mb-0">Anzahl: {transaction.amount}</p>
                    </div>
                    <button type="button" className="btn btn-primary mt-auto" onClick={handleShow}>
                        <small>Details</small>
                    </button>
                </div>
            </a>

            {showModal && (
                <>
                <div className="modal fade show" id={transaction.id} tabIndex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true" style={{ display: 'block' }}>
                    <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">{transaction.stock.name}</h5>
                                <button type="button" className="btn-close" aria-label="Close" onClick={handleClose}></button>
                            </div>
                            <div className="modal-body">
                                <p>
                                    Transaktionstyp: {transaction.transaction_type}<br />
                                    Status: {transaction.status}<br />
                                    Anzahl: {transaction.amount}<br />
                                    Preis: {transaction.price}€<br />
                                    Aktienwert: {transaction.amount * transaction.price}€<br />
                                    Gebühren: {transaction.fee}€<br />
                                    Gesamtpreis: {transaction.total_price}€<br />
                                </p>
                                <div className="mb-3">
                                    <label htmlFor="exampleFormControlTextarea1" className="form-label">Notiz:</label>
                                    <textarea
                                        className="form-control"
                                        id="exampleFormControlTextarea1"
                                        rows="4"
                                        value={newDescription}
                                        onChange={(e) => setNewDescription(e.target.value)}
                                        maxLength="1000"
                                        placeholder="Hier kannst du eine Notiz zu dieser Transaktion hinzufügen."
                                    />
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={handleClose}>Schließen</button>
                                <button type="button" className="btn btn-primary" onClick={handleSubmit}>Speichern</button>
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