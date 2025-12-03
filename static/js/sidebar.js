function toggleSidebar() {
  const sidebar = document.getElementById("sidebar");
  const sidebarTexts = document.querySelectorAll(".sidebar-text");
  const toggleBtn = document.querySelector(".sidebar-toggle svg");

  sidebar.classList.toggle("!w-20");

  sidebarTexts.forEach((text) => {
    text.classList.toggle("hidden");
  });

  // Rotate toggle button icon
  if (sidebar.classList.contains("!w-20")) {
    toggleBtn.style.transform = "rotate(180deg)";
  } else {
    toggleBtn.style.transform = "rotate(0deg)";
  }
}
