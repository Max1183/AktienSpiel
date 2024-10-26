function NavigationButton({ children, active, onclick }) {
    return <button
            className={`list-group-item list-group-item-action list-group-item-primary text-center ${active === children ? 'active' : ''}`}
            onClick={onclick}>
        {children}
    </button>
}

export default NavigationButton
