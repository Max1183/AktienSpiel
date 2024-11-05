function NavigationButton({ children, active, onClick }) {
    return <button
            className={`list-group-item list-group-item-action list-group-item-primary text-center ${active === children ? 'active' : ''}`}
            onClick={onClick}>
        {children}
    </button>
}

export default NavigationButton
