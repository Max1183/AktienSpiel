import Pagination from '../components/Layout/Pagination'
import React, { useState, useEffect } from 'react';
import { getRequest, formatCurrency } from '../utils/helpers';
import LoadingSite from '../components/Loading/LoadingSite';
import { useAlert } from '../components/Alerts/AlertProvider';

function Contest() {
    const [rankingData, setRankingData] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const [totalPages, setTotalPages] = useState(1);
    const [rankingCache, setRankingCache] = useState({});
    const [isLoading, setIsLoading] = useState(true);
    const { addAlert } = useAlert();

    useEffect(() => {
        const fetchRankingData = async () => {
            if (rankingCache[currentPage]) {
                const cachedData = rankingCache[currentPage];
                setRankingData(cachedData.results);
                setTotalPages(cachedData.num_pages)
            } else {
                getRequest(`/api/ranking/?page=${currentPage}`, setIsLoading)
                    .then(data => {
                        setRankingData(data.results)
                        setTotalPages(data.num_pages)
                        rankingCache[currentPage] = data;
                    }).catch(error => {
                        addAlert(error.message, 'danger');
                        setRankingData([]);
                    });
            }
        };
        fetchRankingData();
    }, [currentPage]);

    const handlePageChange = (page) => {
        setCurrentPage(page);
    };

    return <>
        <div className="bg-primary-subtle p-3 shadow rounded p-3">
            <h1>Rangliste:</h1>
            <table className="table table-bordered table-hover">
                <thead>
                    <tr className="table-secondary">
                        <th scope="col">Platz</th>
                        <th scope="col">Team-Name</th>
                        <th scope="col">Gesamtdepotwert</th>
                        <th scope="col">Performance (%)</th>
                    </tr>
                </thead>
                <tbody>
                    {rankingData && rankingData.map((team) => (
                        <tr key={team.id}>
                            <th scope="row">{team.rank}</th>
                            <td>{team.name}</td>
                            <td>{formatCurrency(team.total_balance)}</td>
                            <td>{(team.total_balance / 100000 * 100 - 100).toFixed(2) + "%"}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
            {isLoading ?
                <LoadingSite /> :
                <Pagination currentPage={currentPage} totalPages={totalPages} onPageChange={handlePageChange} />
            }
        </div>
    </>
}

export default Contest
