import { useAlert } from './AlertProvider';
import Alert from './Alert';

const AlertList = () => {
    const { alerts, removeAlert } = useAlert();

    return <>
        {alerts.map((alert) => (
            <Alert key={alert.id} alert={alert} removeAlert={removeAlert} />
        ))}
    </>;
};

export default AlertList;
