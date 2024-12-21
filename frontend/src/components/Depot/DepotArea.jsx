import React, { useState, useEffect } from 'react'
import LoadingSite from '../Loading/LoadingSite';
import ReloadButton from './ReloadButton';

const DepotArea = ({ title, value, handleReload, size, children }) => {
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if(!value) handleReload(setIsLoading);
    }, []);

    return <div className={`col-lg-${size} p-2`}>
        <div className="bg-primary-subtle p-3 shadow rounded p-3 h-100">
            <ReloadButton title={title} handleReload={() => {handleReload(setIsLoading)}} />
            {isLoading ? <LoadingSite /> : (
                !value ? <p className='fs-5 text-danger'>Fehler beim Laden!</p> : children
            )}
        </div>
    </div>
}

export default DepotArea;
