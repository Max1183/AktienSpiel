import React, { useEffect, useRef } from 'react'
import LoadingSite from '../Loading/LoadingSite';
import ReloadButton from './ReloadButton';
import { useOutletContext } from 'react-router-dom';

const DepotArea = ({ title, key1, handleReload=null, size="12", reloadButton=true, children }) => {
    const { loadValue, getLoading, getData } = useOutletContext();
    const onReload = handleReload ? handleReload : () => {loadValue(key1)}
    const isInitialMount = useRef(true);

    useEffect(() => {
        if (isInitialMount.current) {
            isInitialMount.current = false;
            if(!getData(key1) && !getLoading(key1)) onReload();
        }
    }, [key1, loadValue, getData]);

    return <div className={`col-lg-${size} p-2`}>
        <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
            {reloadButton ? (
                <ReloadButton title={title} handleReload={onReload} loading={getLoading(key1)} />
            ) : (
                <h2>{title}</h2>
            )}
            {getLoading(key1) ? <LoadingSite /> : (
                !getData(key1) ? <p className='fs-5 text-danger'>Fehler beim Laden!</p> : children
            )}
        </div>
    </div>
}

export default DepotArea;
