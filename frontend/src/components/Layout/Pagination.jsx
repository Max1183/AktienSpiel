import React, { useState, useEffect } from "react";

function Pagination({ totalPages, currentPage, onPageChange }) {
    const [pageNumbers, setPageNumbers] = useState([]);

    useEffect(() => {
        const calculatePageNumbers = () => {
            if (totalPages <= 1) return [];

            let pages = [];
            if (totalPages < 5) {
                pages = Array.from(
                    { length: totalPages },
                    (_, index) => index + 1
                );
            } else {
                const middlePage =
                    currentPage < 4
                        ? 3
                        : currentPage > totalPages - 3
                        ? totalPages - 2
                        : currentPage;
                pages = [
                    1,
                    middlePage - 1,
                    middlePage,
                    middlePage + 1,
                    totalPages,
                ];
            }
            return pages;
        };

        setPageNumbers(calculatePageNumbers());
    }, [currentPage, totalPages]);

    if (totalPages <= 1) return null;

    return (
        <div className="mt-3">
            <nav aria-label="Page navigation example mt-3">
                <ul className="pagination justify-content-center m-0">
                    {pageNumbers.map((pageNumber) => (
                        <li
                            key={pageNumber}
                            className={`page-item ${
                                pageNumber === currentPage && "active"
                            }`}
                        >
                            <a
                                className="page-link"
                                href="#"
                                onClick={() => {
                                    onPageChange(pageNumber);
                                }}
                            >
                                {pageNumber}
                            </a>
                        </li>
                    ))}
                </ul>
            </nav>
        </div>
    );
}

export default Pagination;
