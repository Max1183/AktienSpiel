import React, { createContext, useContext, useState } from 'react';

const AlertContext = createContext();

export const AlertProvider = ({ children }) => {
    const [alerts, setAlerts] = useState([]);

    const addAlert = (message, type = 'info') => {
        const newAlert = { id: Date.now(), message, type };
        setAlerts([...alerts, newAlert]);
    };

    const removeAlert = (id) => {
        setAlerts(alerts.filter((alert) => alert.id !== id));
    };

    return (
        <AlertContext.Provider value={{ alerts, addAlert, removeAlert }}>
            {children}
        </AlertContext.Provider>
    );
};

export const useAlert = () => {
    return useContext(AlertContext);
};
