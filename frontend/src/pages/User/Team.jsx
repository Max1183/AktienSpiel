import React, { useState } from "react";
import ProfileNavigation from "../../components/Navigation/ProfileNavigation";
import Area from "../../components/General/Area";
import { formatCurrency } from "../../utils/helpers";
import { useAlert } from "../../components/Alerts/AlertProvider";
import { useOutletContext } from "react-router-dom";
import LoadingSite from "../../components/Loading/LoadingSite";
import api from "../../api";
import FormField from "../../components/General/FormField";

function Team() {
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({});
    const [isLoading, setIsLoading] = useState(false);
    const { loadValue } = useOutletContext();
    const { addAlert } = useAlert();

    const handleEdit = () => {
        setFormData({});
        setIsEditing(true);
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSave = async () => {
        if (Object.keys(formData).length === 0) {
            setIsEditing(false);
            return;
        }

        console.log(formData);

        setIsLoading(true);

        try {
            const response = await api.put("/api/team/update/", formData);
            if (response.status === 200) {
                addAlert("Team erfolgreich aktualisiert", "success");
            }
        } catch (error) {
            const data = error.response.data;
            if (error.status === 400 && data) {
                addAlert(`${Object.values(data)[0]}`, "danger");
            } else {
                addAlert("Fehler beim Aktualisieren des Teams", "danger");
            }
        } finally {
            setIsLoading(false);
            setIsEditing(false);
            loadValue("team");
        }
    };

    const canEdit = (team) => {
        return team.edit_timeout <= 0;
    };

    return (
        <>
            <ProfileNavigation />
            <Area title="Mein Team" key1="team" size={isEditing ? "12" : "6"}>
                {({ value: team }) =>
                    !isLoading ? (
                        <>
                            {isEditing ? (
                                <form className="row g-3 mb-3">
                                    <FormField
                                        label="Teamname"
                                        name="name"
                                        value={formData.name}
                                        onChange={handleChange}
                                        placeholder={team.name}
                                        showError={false}
                                        width="col-md-6"
                                    />
                                    <div className="form-group col-md-6">
                                        <label
                                            className="form-label"
                                            htmlFor={"admin"}
                                        >
                                            {"Team Admin"}
                                        </label>
                                        <select
                                            className="form-select"
                                            aria-label="Default select example"
                                            id="admin"
                                            name="admin"
                                            onChange={handleChange}
                                        >
                                            <option
                                                selected
                                                value={team.admin.id}
                                            >
                                                {team.admin}
                                            </option>
                                            {team.members.map(
                                                (member) =>
                                                    member.username !==
                                                        team.admin && (
                                                        <option
                                                            key={member.id}
                                                            value={member.id}
                                                        >
                                                            {member.username}
                                                        </option>
                                                    )
                                            )}
                                        </select>
                                    </div>
                                </form>
                            ) : (
                                <>
                                    <p className="fs-5 mt-3 mb-2">
                                        Teamname: {team.name}
                                        <br />
                                        Teamchef:{" "}
                                        {`${team.admin} ${
                                            team.is_admin ? "(Du)" : ""
                                        }`}
                                        <br />
                                        Barbestand:{" "}
                                        {formatCurrency(team.balance)}
                                        <br />
                                        Gesamtdepotwert:{" "}
                                        {formatCurrency(team.portfolio_value)}
                                        <br />
                                        Trades: {team.trades}
                                        <br />
                                        Platz {team.rank}
                                    </p>
                                    {!canEdit(team) && team.is_admin && (
                                        <p className="text-danger m-0">
                                            Zeit bis zu nächster Änderung:{" "}
                                            {Math.ceil(team.edit_timeout / 60)}{" "}
                                            Minuten
                                        </p>
                                    )}
                                </>
                            )}
                            <div className="d-flex justify-content-between">
                                {isEditing ? (
                                    <>
                                        <button
                                            type="button"
                                            className="btn btn-success"
                                            onClick={handleSave}
                                        >
                                            Speichern
                                        </button>
                                        <button
                                            type="button"
                                            className="btn btn-danger"
                                            onClick={() => setIsEditing(false)}
                                        >
                                            Abbrechen
                                        </button>
                                    </>
                                ) : (
                                    team.is_admin && (
                                        <button
                                            type="button"
                                            className={`btn btn-primary mt-3 ${
                                                !canEdit(team) && "disabled"
                                            }`}
                                            onClick={() => handleEdit(team)}
                                        >
                                            Bearbeiten
                                        </button>
                                    )
                                )}
                            </div>
                        </>
                    ) : (
                        <LoadingSite />
                    )
                }
            </Area>
            {!isEditing && (
                <Area title="Team-Mitglieder" value1="team" size="6">
                    {({ value: team }) =>
                        team && (
                            <>
                                <ul className="list-group mt-3">
                                    {team.members.map((member) => (
                                        <li
                                            key={member.id}
                                            className="list-group-item"
                                        >{`${
                                            team.admin === member.username
                                                ? "Admin: "
                                                : ""
                                        }${member.username} (${
                                            member.first_name
                                        } ${member.last_name})`}</li>
                                    ))}
                                </ul>
                                <div className="mt-3">
                                    <p className="m-0">
                                        Mit diesem Code können weitere
                                        Mitglieder beitreten:
                                        <strong> {team.code}</strong>
                                    </p>
                                </div>
                            </>
                        )
                    }
                </Area>
            )}
        </>
    );
}

export default Team;
