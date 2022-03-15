function hideAlert()
{
	let alert = document.querySelector(".auth-alert");
	alert.style.opacity = "0";
	// wait for animation to complete
	setTimeout(() => {
		alert.style.display = "none";
		document.querySelector(".alert-spacing").style.display = "none";
	},450);
}