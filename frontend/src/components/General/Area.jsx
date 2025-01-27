import React, { useEffect, useRef } from "react";
import LoadingSite from "../Loading/LoadingSite";
import ReloadButton from "./ReloadButton";
import { useOutletContext } from "react-router-dom";
import Pagination from "../Layout/Pagination";

const Area = ({
    title,
    key1 = null,
    value1 = null,
    id = null,
    pagination = false,
    frontendPagination = false,
    pageSize = 10,
    size = "12",
    reloadButton = true,
    children,
}) => {
    const { loadValue, getLoading, getData } = useOutletContext();
    const isInitialMount = useRef(true);

    const [page, setPage] = React.useState(pagination ? 1 : null);
    const [currentPage, setCurrentPage] = React.useState(1);
    const [numPages, setNumPages] = React.useState(1);

    const handleLoadData = () => loadValue(key1, id, page);
    const data = () => getData(key1 || value1, id, page);
    const isLoading = () => getLoading(key1, id, page);

    useEffect(() => {
        if (!key1) return;
        if (isInitialMount.current) {
            isInitialMount.current = false;
            if (!data() && !isLoading()) handleLoadData();
        }
    }, [key1]);

    function handlePageChange(newPage) {
        if (pagination) {
            if (newPage === page) return;
            setPage(newPage);

            const newPageData = getData(key1, id, newPage);
            const newPageLoading = getLoading(key1, id, newPage);
            if (newPageData || newPageLoading) return;
            loadValue(key1, id, newPage);
        } else if (frontendPagination) {
            setCurrentPage(newPage);
        }
    }

    function getNumPages() {
        if (pagination) {
            const data1 = data();
            if (data1 && data1.num_pages !== numPages) {
                setNumPages(data1.num_pages);
            }
            return numPages;
        } else if (frontendPagination) {
            return Math.ceil(data().length / pageSize);
        } else {
            return 1;
        }
    }

    function getPageValue() {
        if (pagination) {
            return data().results;
        } else if (frontendPagination) {
            const start_index = (currentPage - 1) * pageSize;
            const end_index = start_index + pageSize;
            return data().slice(start_index, end_index);
        } else {
            return data();
        }
    }

    return (
        <div className={`col-lg-${size} p-2`}>
            <div className="bg-primary-subtle shadow rounded p-3 h-100">
                {reloadButton && key1 ? (
                    <ReloadButton
                        title={title}
                        handleReload={handleLoadData}
                        loading={isLoading()}
                    />
                ) : (
                    <h2>{title}</h2>
                )}
                {isLoading() ? (
                    <LoadingSite />
                ) : key1 && !data() ? (
                    <p className="fs-5 text-danger">Fehler beim Laden!</p>
                ) : typeof children === "function" ? (
                    children({ value: getPageValue() })
                ) : (
                    children
                )}
                {(pagination ||
                    (frontendPagination &&
                        data() &&
                        data().length > pageSize)) && (
                    <Pagination
                        currentPage={pagination ? page : currentPage}
                        totalPages={getNumPages()}
                        onPageChange={handlePageChange}
                    />
                )}
            </div>
        </div>
    );
};

export default Area;
