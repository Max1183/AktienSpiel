import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import { useAlert } from '../components/Alerts/AlertProvider';
import { getRequest } from '../utils/helpers';
import { Safe2, Safe2Fill, CartCheck, CartCheckFill, PieChart, PieChartFill, Star, StarFill, Search } from 'react-bootstrap-icons';
import DepotNavigation from '../components/Depot/DepotNavigation';

function Depot() {
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
        <div className="btn-group w-100 mb-3">
            <DepotNavigation to="/depot" name="Depot" icon={<Safe2 />} icon_active={<Safe2Fill />} />
            <DepotNavigation to="/depot/transactions" name="Transaktionen" icon={<CartCheck />} icon_active={<CartCheckFill />} />
            <DepotNavigation to="/depot/analysis" name="Auswertung" icon={<PieChart />} icon_active={<PieChartFill />} />
            <DepotNavigation to="/depot/watchlist" name="Watchlist" icon={<Star />} icon_active={<StarFill />} />
            <DepotNavigation to="/depot/search" name="Suchen" icon={<Search />} icon_active={<Search />} />
        </div>
        <div className="row">
            <Outlet context={{
                loadValue: loadValue,
                getLoading: getLoading,
                getData: getData,
            }} />
        </div>
    </>;
}

export default Depot
