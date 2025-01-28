import React, { useState } from "react";
import { formatCurrency } from "../../utils/helpers";
import Area from "../../components/General/Area";

function Contest() {
    const [showModal, setShowModal] = useState(false);
    const [modalTeam, setModalTeam] = useState(null);

    const handleClose = () => setShowModal(false);
    const handleShow = (e, team) => {
        e.preventDefault();
        setModalTeam(team);
        setShowModal(true);
    };

    return (
        <>
            <Area title={"Rangliste"} pagination={true} key1="ranking">
                {({ value: rankingData }) => (
                    <div className="table-responsive">
                        <table className="table table-bordered table-hover m-0">
                            <thead>
                                <tr className="table-secondary">
                                    <th scope="col">Platz</th>
                                    <th scope="col">Team-Name</th>
                                    <th scope="col">Gesamter Depotwert</th>
                                    <th scope="col">Performance</th>
                                </tr>
                            </thead>
                            <tbody>
                                {rankingData &&
                                    rankingData.map((team) => (
                                        <tr
                                            key={team.id}
                                            onClick={(e) => {
                                                handleShow(e, team);
                                            }}
                                        >
                                            <th scope="row">{team.rank}</th>
                                            <td>{team.name}</td>
                                            <td>
                                                {formatCurrency(
                                                    team.total_balance
                                                )}
                                            </td>
                                            <td>
                                                {(
                                                    (team.total_balance /
                                                        100000) *
                                                        100 -
                                                    100
                                                ).toFixed(2) + "%"}
                                            </td>
                                        </tr>
                                    ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </Area>
            {showModal && (
                <>
                    <div
                        className="modal fade show"
                        id={modalTeam.id}
                        tabIndex="-1"
                        aria-labelledby="exampleModalLabel"
                        aria-hidden="true"
                        style={{ display: "block" }}
                    >
                        <div className="modal-dialog modal-dialog-centered modal-dialog-scrollable">
                            <div className="modal-content">
                                <div className="modal-header">
                                    <h5 className="modal-title">
                                        {modalTeam.name}
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
                                        Rang: {modalTeam.rank}
                                        <br />
                                        Gesamter Depotwert:{" "}
                                        {formatCurrency(
                                            modalTeam.total_balance
                                        )}
                                        <br />
                                        Performance:{" "}
                                        {(
                                            (modalTeam.total_balance / 100000) *
                                                100 -
                                            100
                                        ).toFixed(2) + "%"}
                                    </p>
                                    <p className="mb-0">Mitglieder:</p>
                                    <ul>
                                        {modalTeam.members.map((member) => (
                                            <li
                                                key={member.id}
                                            >{`${member.username} (${member.first_name} ${member.last_name})`}</li>
                                        ))}
                                    </ul>
                                    {modalTeam.stocks.length > 0 ? (
                                        <>
                                            <p className="mb-0">Aktien:</p>
                                            <ul className="mb-0">
                                                {modalTeam.stocks.map(
                                                    (stock) => (
                                                        <li key={stock.id}>
                                                            {stock.name}
                                                        </li>
                                                    )
                                                )}
                                            </ul>
                                        </>
                                    ) : (
                                        <>
                                            <p className="mb-0">
                                                Dieser Spieler besitzt derzeit
                                                keine Aktien.
                                            </p>
                                        </>
                                    )}
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

export default Contest;
