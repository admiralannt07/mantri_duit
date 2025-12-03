function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const toggleBtn = document.querySelector(".sidebar-toggle svg");

  sidebar.classList.toggle("!w-20");
  
  if (sidebar.classList.contains("!w-20")) {
    sidebar.setAttribute("data-collapsed", "true");
    toggleBtn.style.transform = "rotate(180deg)";
  } else {
    sidebar.removeAttribute("data-collapsed");
    toggleBtn.style.transform = "rotate(0deg)";
  }
}
