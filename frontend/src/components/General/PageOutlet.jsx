import React, { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import { useAlert } from "../Alerts/AlertProvider";
import { getRequest } from "../../utils/helpers";
import DepotNavigation from "../Navigation/DepotNavigation";

function PageOutlet() {
    const { addAlert } = useAlert();
    const [data, setData] = useState({});
    const location = useLocation();

    const loadValue = (key, id = null, page = null) => {
        changeLoading(key, true, id, page);
        getRequest(`/api/${key}/${id ? `${id}/` : page ? `?page=${page}` : ""}`)
            .then((data) => changeData(key, data, id, page))
            .catch((error) => addAlert(error.message, "danger"))
            .finally(() => changeLoading(key, false, id, page));
    };

    const getLoading = (key, id = null, page = null) => {
        const value = data[key];
        if (!value) return null;
        if (id) return value[id]?.isLoading || null;
        if (page) return value[page]?.isLoading || null;
        return value.isLoading || null;
    };

    const getData = (key, id = null, page = null) => {
        const value = data[key];
        if (!value) return undefined;
        if (id) return value[id]?.data;
        if (page) return value[page]?.data;
        return value.data;
    };

    const changeLoading = (key, newIsLoading, id = null, page = null) => {
        setData((prevData) => ({
            ...prevData,
            [key]: {
                ...prevData[key],
                ...(id !== null
                    ? {
                          [id]: {
                              ...prevData[key]?.[id],
                              isLoading: newIsLoading,
                          },
                      }
                    : page !== null
                    ? {
                          [page]: {
                              ...prevData[key]?.[page],
                              isLoading: newIsLoading,
                          },
                      }
                    : { isLoading: newIsLoading }),
            },
        }));
    };

    const changeData = (key, newData, id = null, page = null) => {
        setData((prevData) => ({
            ...prevData,
            [key]: {
                ...prevData[key],
                ...(id !== null
                    ? { [id]: { ...prevData[key]?.[id], data: newData } }
                    : page !== null
                    ? { [page]: { ...prevData[key]?.[page], data: newData } }
                    : { data: newData }),
            },
        }));
    };

    return (
        <>
            {location.pathname.startsWith("/depot") && <DepotNavigation />}
            <div className="row">
                <Outlet
                    context={{
                        loadValue,
                        getLoading,
                        getData,
                        changeLoading,
                    }}
                />
            </div>
        </>
    );
}

export default PageOutlet;
