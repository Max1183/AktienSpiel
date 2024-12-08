import Pagination from '../components/Layout/Pagination'
import React, { useState } from 'react';

function Contest() {
    const [currentPage, setCurrentPage] = useState(1);

    const handlePageChange = (page) => {
        setCurrentPage(page);
        console.log(`Navigating to page ${page}`);
    };

    return <>
        <div className="bg-primary-subtle p-3 shadow rounded p-3">
            <h1>Rangliste:</h1>
            <Pagination currentPage={currentPage} totalPages={10} onPageChange={handlePageChange} />
        </div>
    </>
}

export default Contest
