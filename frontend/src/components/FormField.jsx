const FormField = ({ label, type, name, value, onChange, onBlur, error, width }) => {
    return (
        <div className={`form-group ${width ? width : 'col-12'}`}>
            <label className="form-label" htmlFor={name}>{label}</label>
            <input
                type={type}
                id={name}
                name={name}
                value={value}
                onChange={onChange}
                onBlur={onBlur}
                className={`form-control ${error ? 'is-invalid' : 'is-valid'}`}
            />
            <div className="invalid-feedback">{error}</div>
            <div className="valid-feedback">Sieht gut aus!</div>
        </div>
    );
};

export default FormField;
