import { QuestionCircleFill } from 'react-bootstrap-icons';

const Tooltip = ({ text }) => {
    return <div className="ms-2" data-bs-toggle="tooltip" data-bs-placement="top" data-bs-title={text}>
        <QuestionCircleFill />
    </div>;
};

export default Tooltip;
