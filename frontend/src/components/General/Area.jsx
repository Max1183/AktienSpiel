import React, { useEffect, useRef } from "react";
import LoadingSite from "../Loading/LoadingSite";
import ReloadButton from "./ReloadButton";
import { useOutletContext } from "react-router-dom";
import Pagination from "../Layout/Pagination";

const Area = ({
    title,
    key1,
    id = null,
    pagination = false,
    size = "12",
    reloadButton = true,
    children,
}) => {
    const { loadValue, getLoading, getData } = useOutletContext();
    const [page, setPage] = React.useState(pagination ? 1 : null);
    const [numPages, setNumPages] = React.useState(1);
    const isInitialMount = useRef(true);

    const handleLoadData = () => loadValue(key1, id, page);
    const data = () => getData(key1, id, page);
    const isLoading = () => getLoading(key1, id, page);

    useEffect(() => {
        if (!key1) return;
        if (isInitialMount.current) {
            isInitialMount.current = false;
            if (!data() && !isLoading()) handleLoadData();
        }
    }, [key1, isLoading, data, handleLoadData]);

    function handlePageChange(newPage) {
        if (newPage === page) return;
        setPage(newPage);

        const newPageData = getData(key1, id, newPage);
        const newPageLoading = getLoading(key1, id, newPage);
        if (newPageData || newPageLoading) return;
        loadValue(key1, id, newPage);
    }

    function getNumPages() {
        const data1 = data();
        if (data1 && data1.num_pages !== numPages) {
            setNumPages(data1.num_pages);
        }
        return numPages;
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
                    children({ value: pagination ? data().results : data() })
                ) : (
                    children
                )}
                {pagination && (
                    <Pagination
                        currentPage={page}
                        totalPages={getNumPages()}
                        onPageChange={handlePageChange}
                    />
                )}
            </div>
        </div>
    );
};

export default Area;
