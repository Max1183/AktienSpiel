import React, { useState, useEffect } from 'react';
import ProfileLayout from '../components/ProfileLayout';
import LoadingSite from '../components/Loading/LoadingSite';
import { getRequest } from '../utils/helpers';
import { useAlert } from '../components/Alerts/AlertProvider';
import { formatCurrency } from '../utils/helpers';

function Team() {
    const [team, setTeam] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        getRequest('/api/team/', setIsLoading)
            .then(data => setTeam(data))
            .catch(error => addAlert(error.message, 'danger'));
    }, []);

    if (isLoading) return <ProfileLayout>
        <LoadingSite />
    </ProfileLayout>

    if (!team) return <ProfileLayout>
        <h2>Fehler beim Laden des Teams!</h2>
    </ProfileLayout>

    return <ProfileLayout>
        <div className="row">
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Mein Team</h2>
                    <p className="fs-5 mt-3 mb-0">
                        Teamname: {team.name}<br />
                        Barbestand: {formatCurrency(team.balance)}<br />
                        Gesamtdepotwert: {formatCurrency(team.portfolio_value)}<br />
                        Trades: {team.trades}<br />
                        Platz {team.rank}
                    </p>
                </div>
            </div>
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Team-Mitglieder</h2>
                    <ul className="list-group mt-3">
                        {team.members.map((member) => (
                            <li key={member.id} className="list-group-item">{`${member.username} (${member.first_name} ${member.last_name})`}</li>
                        ))}
                    </ul>
                    <div className="mt-3">
                        <p className="m-0">
                            Mit diesem Code können weitere Mitglieder beitreten:
                            <strong> {team.code}</strong>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </ProfileLayout>
}

export default Team
