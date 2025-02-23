const FormField = ({
    label,
    type = "text",
    name,
    value,
    onChange,
    onBlur,
    error,
    width = "col-12",
    placeholder = "",
    showError = true,
}) => {
    return (
        <div className={`form-group ${width}`}>
            <label className="form-label" htmlFor={name}>
                {label}
            </label>
            <input
                type={type}
                id={name}
                name={name}
                value={value}
                onChange={onChange}
                onBlur={onBlur}
                placeholder={placeholder}
                className={`form-control ${
                    showError && (error ? "is-invalid" : "is-valid")
                }`}
            />
            {showError && (
                <>
                    <div className="invalid-feedback">{error}</div>
                    <div className="valid-feedback">Sieht gut aus!</div>
                </>
            )}
        </div>
    );
};

export default FormField;
