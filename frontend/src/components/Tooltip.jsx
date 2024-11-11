const Tooltip = ({ text }) => {
    return <img
        className="ms-2"
        width="15"
        height="15"
        src="/Tooltip.png"
        data-bs-toggle="tooltip"
        data-bs-placement="top"
        data-bs-title={text}
    />
};

export default Tooltip;
