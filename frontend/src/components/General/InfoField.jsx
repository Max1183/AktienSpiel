function InfoField({ label, value }) {
    return (
        <div className="col-4">
            <div className="card p-3 h-100">
                <p className="mb-0 fw-bold mb-auto">{value}</p>
                <small>{label}</small>
            </div>
        </div>
    );
}

export default InfoField;
