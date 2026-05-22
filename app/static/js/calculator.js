function calculateConsumption() {
	const area = parseFloat(document.getElementById('area').value) || 0
	const coefficient =
		parseFloat(document.getElementById('coefficient').value) || 1
	const result = area * coefficient
	document.getElementById('result').textContent = result.toFixed(2)
}

document.addEventListener('DOMContentLoaded', function () {
	const inputs = document.querySelectorAll('#area, #coefficient')
	inputs.forEach(function (input) {
		input.addEventListener('input', calculateConsumption)
	})
})
