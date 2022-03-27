const cmp = (inx,asc) => (rowA,rowB) => {
	const conA = rowA.children[inx].innerText
	const conB = rowB.children[inx].innerText
	const isANum = !isNaN(conA);
	const isBNum = !isNaN(conB);
	if(isANum && isBNum)
	{
		if(asc)
			return conA - conB
		return conB - conA	
	}
	if(asc)
		return conA.localeCompare(conB)
	return conB.localeCompare(conA)
};

window.onload = () => {
	const tables = document.querySelectorAll(".sorting");

	for(const table of tables)
	{
		const headers = table.querySelectorAll(".header-el");
		for(let i = 0;i < headers.length;i++)
		{
			const sortBtn = headers[i].querySelector(".sort-btn");

			const sortCmpAsc = cmp(i,true);
			const sortCmpDesc = cmp(i,false);
			sortBtn.addEventListener("click",() => {
				const classes = sortBtn.classList

				let rows = Array.from(table.querySelectorAll(".data-row"));
				if(classes.contains("line"))
				{
					// sort asc and clear sorts on other columns
					for(let j = 0;j < headers.length;j++)
					{
						const otherSortBtn = headers[j].querySelector(".sort-btn");
						if(otherSortBtn.classList.contains("uparrow") || otherSortBtn.classList.contains("downarrow"))
						{
							otherSortBtn.classList.remove("uparrow");
							otherSortBtn.classList.remove("downarrow");
							otherSortBtn.classList.add("line");
							break; // there will only ever be 1 sorted column 
						}
					}
					classes.remove("line");
					rows.sort(sortCmpAsc);
					classes.add("downarrow");

				}
				else if(classes.contains("uparrow"))
				{
					// the table is sorted desc, we sort it asc again
					classes.remove("uparrow");
					rows.sort(sortCmpAsc);
					classes.add("downarrow");

				}
				else if(classes.contains("downarrow"))
				{
					// the table is sorted asc now we sort it desc
					classes.remove("downarrow");
					rows.sort(sortCmpDesc);
					classes.add("uparrow");
				}
				rows.forEach((tr) => table.appendChild(tr));
			});
		}
	}
};



