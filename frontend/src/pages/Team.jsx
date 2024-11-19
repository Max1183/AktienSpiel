import React, { useState, useEffect } from 'react';
import ProfileLayout from '../components/ProfileLayout';
import LoadingSite from '../components/Loading/LoadingSite';
import api from '../api';
import { useAlert } from '../components/Alerts/AlertProvider';
import { formatCurrency } from '../utils/helpers';

function Team() {
    const [team, setTeam] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        const getTeam = async () => {
            try {
                const response = await api.get(`/api/team/`);
                setTeam(response.data)
            } catch (error) {
                addAlert(error.message, 'danger');
            } finally {
                setIsLoading(false);
            }
        };

        getTeam();
    }, [])

    if (isLoading) return <ProfileLayout>
        <LoadingSite />;
    </ProfileLayout>

    if (!team) return <ProfileLayout>
        <h2>Fehler beim Laden des Teams!</h2>
    </ProfileLayout>

    return <ProfileLayout>
        <div className="row">
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Mein Team</h2>
                    <p className="fs-5 mt-3">
                        Teamname: "{team.name}"<br />
                        Barbestand: {formatCurrency(team.balance)}<br />
                        Gesamtdepotwert: {formatCurrency(team.portfolio_value)}<br />
                        Trades: {team.trades}
                    </p>
                </div>
            </div>
            <div className="col-lg-6 p-2">
                <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
                    <h2>Team-Mitglieder</h2>
                    <ul class="list-group mt-3">
                        {team.members.map((member) => (
                            <li class="list-group-item">{member.name}</li>
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
