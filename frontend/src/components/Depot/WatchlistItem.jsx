import React, { useState } from 'react';
import api from '../../api';
import { formatDate, formatCurrency } from '../../utils/helpers';
import { useAlert } from '../../components/Alerts/AlertProvider';

function WatchlistItem({ watchlist, onDelete }) {
    const [newNote, setNewNote] = useState(watchlist.note ?? "");
    const [showModal, setShowModal] = useState(false);
    const { addAlert } = useAlert();

    const handleClose = () => setShowModal(false);
    const handleShow = (e) => {
        e.preventDefault();
        setShowModal(true);
    }

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (newNote !== watchlist.note) {
            try {
                const res = await api.patch(`/api/watchlist/${watchlist.id}/`, {
                    note: newNote
                });
                if (res.status === 200 || res.status === 201 || res.status === 204) {
                    addAlert('Beschreibung der Watchlist erfolgreich geändert!', 'success');
                } else {
                    addAlert('Fehler beim Ändern der Beschreibung.', 'danger');
                }
            } catch (err) {
                addAlert(err, 'danger');
            }
        }
        handleClose();
    };

    return (
        <>
            <a className="list-group-item list-group-item-action" key={watchlist.id} href={`stocks/${watchlist.stock.id}`}>
                <div className="d-flex w-100 justify-content-between">
                    <h5 className="mb-1">{watchlist.stock.name}</h5>
                    <small className="text-muted">{formatDate(watchlist.date)}</small>
                </div>
                <div className="d-flex w-100 justify-content-between">
                    <div>
                        <p className="mb-1">Preis: {formatCurrency(watchlist.stock.current_price)}</p>
                    </div>
                    <div>
                        <button type="button" className="btn btn-primary mt-auto me-1" onClick={handleShow}>
                            <small>Details</small>
                        </button>
                        <button type="button" className="btn btn-danger mt-auto" onClick={(e) => onDelete(e, watchlist.id)}>
                            <small>Löschen</small>
                        </button>
                    </div>
                </div>
            </a>

            {showModal && (
                <>
                <div className="modal fade show" id={watchlist.id} tabIndex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true" style={{ display: 'block' }}>
                    <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                        <div className="modal-content">
                            <div className="modal-header">
                                <h5 className="modal-title">{watchlist.stock.name}</h5>
                                <button type="button" className="btn-close" aria-label="Close" onClick={handleClose}></button>
                            </div>
                            <div className="modal-body">
                                <p>
                                    Preis: {formatCurrency(watchlist.stock.current_price)}<br />
                                    Datum: {formatDate(watchlist.date)}<br />
                                </p>
                                <div className="mb-3">
                                    <label htmlFor="exampleFormControlTextarea1" className="form-label">Notiz:</label>
                                    <textarea
                                        className="form-control"
                                        id="exampleFormControlTextarea1"
                                        rows="4"
                                        value={newNote}
                                        onChange={(e) => setNewNote(e.target.value)}
                                        maxLength="1000"
                                        placeholder="Hier kannst du eine Notiz zu dieser Watchlist hinzufügen."
                                    />
                                </div>

                            </div>
                            <div className="modal-footer d-flex justify-content-between">
                                <button type="button" className="btn btn-danger mt-auto" onClick={(e) => onDelete(e, watchlist.id)}>Löschen</button>
                                <button type="button" className="btn btn-secondary" onClick={handleClose}>Schließen</button>
                                <button type="button" className="btn btn-success" onClick={handleSubmit}>Speichern</button>
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

export default WatchlistItem;
