document.addEventListener('DOMContentLoaded', function () {
	const mapBlock = document.getElementById('warehouse-map')
	if (!mapBlock) {
		return
	}

	const warehouses = JSON.parse(mapBlock.dataset.warehouses || '[]')

	warehouses.forEach(function (warehouse) {
		const item = document.createElement('div')
		item.className = 'warehouse-item'
		item.innerHTML =
			'<strong>' + warehouse.name + '</strong><br>' + warehouse.address
		mapBlock.appendChild(item)
	})
})
