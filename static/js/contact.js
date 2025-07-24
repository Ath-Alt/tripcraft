document.addEventListener("DOMContentLoaded", function() {
    const formBtn = document.getElementById("form");
    const cancelBtn = document.getElementById("cancel");
    const popup = document.getElementById("dim");

    formBtn.addEventListener("click", function() {
        popup.style.display = "block";
    });

    cancelBtn.addEventListener("click", function() {
        popup.style.display = "none";
    });
});