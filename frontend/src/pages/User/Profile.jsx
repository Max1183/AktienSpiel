import React from "react";
import ProfileNavigation from "../../components/Navigation/ProfileNavigation";
import Area from "../../components/General/Area";
import FormField from "../../components/General/FormField";
import api from "../../api";
import { useAlert } from "../../components/Alerts/AlertProvider";
import LoadingSite from "../../components/Loading/LoadingSite";
import { useOutletContext } from "react-router-dom";

function Profile() {
    const [isEditing, setIsEditing] = React.useState(false);
    const [formData, setFormData] = React.useState({});
    const [isLoading, setIsLoading] = React.useState(false);
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

        setIsLoading(true);

        try {
            const response = await api.put("/api/profile/update/", formData);
            if (response.status === 200) {
                addAlert("Profil erfolgreich aktualisiert", "success");
            }
        } catch (error) {
            const data = error.response.data;
            if (error.status === 400 && data) {
                addAlert(`${Object.values(data)[0]}`, "danger");
            } else {
                addAlert("Fehler beim Aktualisieren des Profils", "danger");
            }
        } finally {
            setIsLoading(false);
            setIsEditing(false);
            loadValue("profile");
        }
    };

    return (
        <>
            <ProfileNavigation />
            <Area title="Profil" key1="profile">
                {({ value: profile }) =>
                    !isLoading ? (
                        <>
                            {isEditing ? (
                                <form className="row g-3 mb-3">
                                    <FormField
                                        label="Benutzername"
                                        name="username"
                                        value={formData.username}
                                        onChange={handleChange}
                                        placeholder={profile.user.username}
                                        showError={false}
                                        width="col-md-6"
                                    />
                                    <FormField
                                        label="Email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleChange}
                                        placeholder={profile.user.email}
                                        showError={false}
                                        width="col-md-6"
                                    />
                                    <FormField
                                        label="Vorname"
                                        name="first_name"
                                        value={formData.first_name}
                                        onChange={handleChange}
                                        placeholder={profile.user.first_name}
                                        showError={false}
                                        width="col-md-6"
                                    />
                                    <FormField
                                        label="Nachname"
                                        name="last_name"
                                        value={formData.last_name}
                                        onChange={handleChange}
                                        placeholder={profile.user.last_name}
                                        showError={false}
                                        width="col-md-6"
                                    />
                                </form>
                            ) : (
                                <p className="fs-5 mt-3">
                                    Nutzername: {profile.user.username}
                                    <br />
                                    Teamname: {profile.team}
                                    <br />
                                    Vorname: {profile.user.first_name}
                                    <br />
                                    Nachname: {profile.user.last_name}
                                    <br />
                                    E-Mail: {profile.user.email}
                                    <br />
                                </p>
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
                                    <button
                                        type="button"
                                        className="btn btn-primary"
                                        onClick={() => handleEdit(profile)}
                                    >
                                        Bearbeiten
                                    </button>
                                )}
                                <a href="/logout" className="btn btn-primary">
                                    Logout
                                </a>
                            </div>
                        </>
                    ) : (
                        <LoadingSite />
                    )
                }
            </Area>
        </>
    );
}

export default Profile;
