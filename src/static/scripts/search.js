window.onload = () => {
	let form = document.querySelector(".search-form");
	let searchBar = form.querySelector(".search-bar");

	form.querySelector(".users-opt").addEventListener("click",() => {
		searchBar.value = "";
		searchBar.setAttribute("list","users");
		searchBar.setAttribute("placeholder","Uporabnik");
	});

	form.querySelector(".repos-opt").addEventListener("click",() => {
		searchBar.value = "";
		searchBar.setAttribute("list","repos");
		searchBar.setAttribute("placeholder","Repozitorij");
	});
}