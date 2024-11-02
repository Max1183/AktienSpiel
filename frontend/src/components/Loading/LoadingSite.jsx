import Layout from '../Layout/Layout';
import LoadingIndicator from './LoadingIndicator';

function LoadingSite ({ withLayout = true }) {
    return withLayout ? (
        <Layout>
            <div className="d-flex justify-content-center align-items-center">
                <LoadingIndicator />
            </div>
        </Layout>
    ) : (
        <div className="d-flex justify-content-center align-items-center">
            <LoadingIndicator />
        </div>
    )
}

export default LoadingSite
