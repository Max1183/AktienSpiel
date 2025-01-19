import React from 'react';
import ProfileNavigation from '../../components/Navigation/ProfileNavigation';
import Area from '../../components/General/Area';
import { useOutletContext } from 'react-router-dom';
import { formatCurrency } from '../../utils/helpers';

function Team() {
    const { getData } = useOutletContext();

    return <>
        <ProfileNavigation />
        <Area title="Mein Team" key1="team" size='6'>
            {getData("team") && <p className="fs-5 mt-3 mb-0">
                Teamname: {getData("team").name}<br />
                Barbestand: {formatCurrency(getData("team").balance)}<br />
                Gesamtdepotwert: {formatCurrency(getData("team").portfolio_value)}<br />
                Trades: {getData("team").trades}<br />
                Platz {getData("team").rank}
            </p>}
        </Area>
        <Area title="Team-Mitglieder" size='6'>
            {getData("team") && <>
                <ul className="list-group mt-3">
                    {getData("team").members.map((member) => (
                        <li key={member.id} className="list-group-item">{`${member.username} (${member.first_name} ${member.last_name})`}</li>
                    ))}
                </ul>
                <div className="mt-3">
                    <p className="m-0">
                        Mit diesem Code können weitere Mitglieder beitreten:
                        <strong> {getData("team").code}</strong>
                    </p>
                </div>
            </>}
        </Area>
    </>
}

export default Team
