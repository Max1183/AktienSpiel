import {useState} from 'react'
import Layout from '../components/Layout'
import '../styles/Home.css'
import api from '../api'

function CreateStatistic() {
    const [description, setDescription] = useState('')
    const [name, setName] = useState('')

    const createStatistic = (e) => {
        e.preventDefault();
        api.post('/api/statistics/', {
            name: name,
            description: description,
        }).then((res) => {
            if (res.status === 201) alert('Statistic created');
            else alert('Failed to create Statistic');
        }).catch((err) => alert(err));
    };

    return <Layout>
        <h2>Create a new statistic</h2>
        <form className="creation-form" onSubmit={createStatistic}>
            <label htmlFor="name">Name:</label>
            <br />
            <input
                type="text"
                id="name"
                name="name"
                required
                onChange={(e) => setName(e.target.value)}
                value={name}
            />
            <label htmlFor="description">Description:</label>
            <br />
            <textarea
                id="description"
                name="description"
                required
                onChange={(e) => setDescription(e.target.value)}
                value={description}
            />
            <br />
            <input type="submit" value="Submit"/>
        </form>
    </Layout>
}

export default CreateStatistic
