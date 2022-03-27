window.onload = () => {
	let form = document.querySelector(".search-form");
	let searchBar = form.querySelector(".search-input");

	let usersOption = form.querySelector(".users-opt");
	let reposOption = form.querySelector(".repos-opt");

	const usersSwap = () => {
		searchBar.value = "";
		searchBar.setAttribute("list","users");
		searchBar.setAttribute("placeholder","Uporabnik");
	};
	const reposSwap = () => {
		searchBar.value = "";
		searchBar.setAttribute("list","repos");
		searchBar.setAttribute("placeholder","Repozitorij");
	};

	usersOption.addEventListener("click",usersSwap);
	reposOption.addEventListener("click",reposSwap);

	// fix for caching problem 
	setTimeout(() => {
		if(usersOption.checked)
		{
			usersSwap();
		}
		else if(reposOption.checked)
		{
			reposSwap();
		}
	},5);
};