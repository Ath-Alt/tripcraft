document.addEventListener("DOMContentLoaded", function () {
  const logoutBtn = document.getElementById("logout");
  const logoutCnclBtn = document.getElementById("logout_cancel");
  const logoutPopup = document.getElementById("logout_dim");
    
  logoutBtn.addEventListener("click", function() {
      logoutPopup.style.display = "block";
  });
  
  logoutCnclBtn.addEventListener("click", function() {
    logoutPopup.style.display = "none";
  });
});