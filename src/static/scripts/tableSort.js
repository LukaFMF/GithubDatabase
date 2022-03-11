function addClickers()
{
	// let headers = Array.from(document.querySelectorAll("th"));
	
	// headers.forEach(item => {
	// 	item.addEventListener("click",event => {
	// 		let table = item.closest("table");
	// 		data = Array.from(table.querySelectorAll("tr").forEach(tr => {
	// 			Array.from(tr.querySelectorAll("td").forEach(td => {td.innerHTML}));
	// 		}));
	// 	})
	// });

	const getCellValue = (tr, idx) => tr.children[idx].innerText || tr.children[idx].textContent;

	const comparer = (idx, asc) => (a, b) => ((v1, v2) => 
		v1 !== '' && v2 !== '' && !isNaN(v1) && !isNaN(v2) ? v1 - v2 : v1.toString().localeCompare(v2)
		)(getCellValue(asc ? a : b, idx), getCellValue(asc ? b : a, idx));

	// do the work...
	document.querySelectorAll('th').forEach(th => th.addEventListener('click',() => {
		const table = th.closest('table');
		Array.from(table.querySelectorAll('tr:nth-child(n+2)'))
			.sort(comparer(Array.from(th.parentNode.children).indexOf(th), this.asc = !this.asc))
			.forEach(tr => table.appendChild(tr));
	}));
}

