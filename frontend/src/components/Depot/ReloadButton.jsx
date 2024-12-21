import React from 'react';
import { ArrowClockwise } from 'react-bootstrap-icons';

const ReloadButton = ({ title, handleReload }) => {
    return <div className='d-flex justify-content-between mb-2'>
        <h2 className='m-0'>{title}</h2>
        <button className="btn btn-primary" onClick={handleReload}>
            <ArrowClockwise />
        </button>
    </div>
}

export default ReloadButton
