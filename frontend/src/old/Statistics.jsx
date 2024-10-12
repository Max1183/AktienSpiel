import {useState, useEffect} from 'react'
import Layout from '../components/Layout'
import Statistic from '../components/Statistic'
import api from '../api'

function Statistics() {
    const [statistics, setStatistics] = useState([])

    useEffect(() => {
        getStatistics()
    }, [])

    const getStatistics = () => {
        api
            .get('/api/statistics/')
            .then((res) => res.data)
            .then((data) => setStatistics(data))
            .catch((err) => alert(err));
    };

    const deleteStatistic = (id) => {
        api.delete(`/api/statistics/delete/${id}/`).then((res) => {
            if (res.status === 204) alert('Statistic deleted');
            else alert('Failed to delete statistic');
            getStatistics();
        }).catch((err) => alert(err));
    };

    return <Layout>
        <h1>Statistics</h1>
        <div>
            {statistics.map((statistic) => (
                <Statistic statistic={statistic} onDelete={deleteStatistic} key={statistic.id} />
            ))}
        </div>
    </Layout>
}

export default Statistics
