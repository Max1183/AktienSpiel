import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAlert } from '../Alerts/AlertProvider';
import { getRequest } from '../../utils/helpers';

function PageOutlet() {
    const { addAlert } = useAlert();

    const [data, setData] = useState({});

    const loadValue = (key, id=null) => {
        changeLoading(key, true);
        getRequest(`/api/${key}/${id ? id + '/' : ''}`)
            .then(data => {changeData(key, data, id)})
            .catch(error => addAlert(error.message, 'danger'))
            .finally(() => changeLoading(key, false));
    }

    const getLoading = (key) => {
        if (!data[key]) return false;
        return data[key].isLoading;
    }

    const getData = (key) => {
        if (!data[key]) return null;
        return data[key].data;
    }

    const changeLoading = (key, newIsLoading) => {
        setData(prevData => ({
            ...prevData,
            [key]: {
                ...prevData[key],
                isLoading: newIsLoading
            }
        }));
    }

    const changeData = (key, newData, id = null) => {
        setData(prevData => {
            const updatedData = {
                ...prevData,
                [key]: {
                    isLoading: false,
                    data: id
                        ? { ...((prevData[key] && prevData[key].data) || {}), [id]: newData }
                        : newData
                }
            };
            return updatedData;
        });
    };

    return <>
        <div className="row">
            <Outlet context={{
                loadValue: loadValue,
                getLoading: getLoading,
                getData: getData,
            }} />
        </div>
    </>;
}

export default PageOutlet
