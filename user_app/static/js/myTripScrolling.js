document.addEventListener("DOMContentLoaded", function () {
    console.log("just seeing ..."); 
    function setupScrollButtons() {
        console.log("Binding scroll buttons..."); 
        // [Az] Scroll functionality for category folders
        const scrollContainer = document.querySelector(".cat-folders");
        const leftBtn = document.querySelector(".left-btn");
        const rightBtn = document.querySelector(".right-btn");

        if (scrollContainer && leftBtn && rightBtn) {
            rightBtn.addEventListener("click", () => {
                scrollContainer.scrollBy({ left: 150, behavior: "smooth" });
            });
            leftBtn.addEventListener("click", () => {
                scrollContainer.scrollBy({ left: -150, behavior: "smooth" });
            });
        }

        // [Az] Scrolling for the Trip list
        const scrolltriplist = document.querySelector(".trip-folders");
        const upBtn = document.querySelector(".up-btn");
        const downBtn = document.querySelector(".down-btn");

        if (scrolltriplist && upBtn && downBtn) {
            const scrollAmount = scrolltriplist.offsetHeight / 2;

            downBtn.addEventListener("click", () => {
                scrolltriplist.scrollBy({ top: scrollAmount, behavior: "smooth" });
            });

            upBtn.addEventListener("click", () => {
                scrolltriplist.scrollBy({ top: -scrollAmount, behavior: "smooth" });
            });
        }
    }

    // [Az] Call when the page first loads
    setupScrollButtons();

    // [Az] Call again after HTMX swaps content
    document.body.addEventListener("htmx:afterSwap", function (evt) {
        console.log("HTMX just swapped content!");
        // setupScrollButtons();
        setTimeout(setupScrollButtons, 10); // Small delay just in case
    });

});
