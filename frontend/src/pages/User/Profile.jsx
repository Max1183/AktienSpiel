import React from "react";
import ProfileNavigation from "../../components/Navigation/ProfileNavigation";
import Area from "../../components/General/Area";
import FormField from "../../components/General/FormField";

function Profile() {
    const [isEditing, setIsEditing] = React.useState(false);
    const [formData, setFormData] = React.useState({
        username: "",
        first_name: "",
        last_name: "",
    });

    const handleEdit = (profile) => {
        setFormData({
            username: profile.user.username,
            first_name: profile.user.first_name,
            last_name: profile.user.last_name,
        });
        setIsEditing(true);
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSave = () => {
        setIsEditing(false);
    };

    return (
        <>
            <ProfileNavigation />
            <Area title="Profil" key1="profile">
                {({ value: profile }) => (
                    <>
                        {isEditing ? (
                            <form className="row g-3 mb-5">
                                <FormField
                                    label="Benutzername"
                                    type="text"
                                    name="username"
                                    value={formData.username}
                                    onChange={handleChange}
                                    showError={false}
                                />
                                <FormField
                                    label="Vorname"
                                    type="text"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    showError={false}
                                    width="col-md-6"
                                />
                                <FormField
                                    label="Benutzername"
                                    type="text"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    showError={false}
                                    width="col-md-6"
                                />
                                {/*<div className="my-3">
                                    <label
                                        htmlFor="username"
                                        className="form-label"
                                    >
                                        Benutzername
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        id="username"
                                        value={formData.username}
                                        onChange={handleChange}
                                    />
                                </div>
                                <div className="row mb-3">
                                    <div className="col">
                                        <label
                                            htmlFor="firstname"
                                            className="form-label"
                                        >
                                            Vorname
                                        </label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            id="firstname"
                                            value={formData.first_name}
                                            onChange={handleChange}
                                        />
                                    </div>
                                    <div className="col">
                                        <label
                                            htmlFor="lastname"
                                            className="form-label"
                                        >
                                            Nachname
                                        </label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            id="lastname"
                                            value={formData.last_name}
                                            onChange={handleChange}
                                        />
                                    </div>
                                </div>*/}
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
                )}
            </Area>
        </>
    );
}

export default Profile;
