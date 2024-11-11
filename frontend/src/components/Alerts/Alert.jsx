const Alert = ({ alert, removeAlert }) => {
    const alertTypeClass = `alert alert-${alert.type} alert-dismissible fade show`;

    return (
        <div className={alertTypeClass} role="alert">
          {alert.message}
          <button type="button" className="btn-close" data-bs-dismiss="alert" aria-label="Close" onClick={() => removeAlert(alert.id)} />
        </div>
    );
};

export default Alert;
