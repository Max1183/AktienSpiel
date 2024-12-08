import React, {useState} from 'react';

function Pagination({ totalPages, currentPage, onPageChange }) {
    const [pageNumbers] = useState([1, 2, 3, 4, totalPages]);

    const middlePage = currentPage < 4 ? 3 : currentPage > totalPages - 3 ? totalPages - 2 : currentPage;

    pageNumbers[1] = middlePage - 1;
    pageNumbers[2] = middlePage;
    pageNumbers[3] = middlePage + 1;

    return (
        <nav aria-label="Page navigation example">
            <ul className="pagination justify-content-center">
                {pageNumbers.map((pageNumber) => (
                    <li className={`page-item ${pageNumber === currentPage && 'active'}`}>
                        <a className="page-link" href="#" onClick={() => {onPageChange(pageNumber)}}>{pageNumber}</a>
                    </li>
                ))}
            </ul>
        </nav>
    );
}

export default Pagination;
