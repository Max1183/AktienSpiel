function StockListItem({ stock }) {
    return <a href={'/depot/stocks/' + stock.id} className="list-group-item list-group-item-action">
        {stock.name} - {stock.current_price}€
    </a>
}

export default StockListItem
