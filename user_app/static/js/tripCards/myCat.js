document.addEventListener("DOMContentLoaded", function () {  
// [Az] Function to convert RGB to Hex
    function rgbToHex(rgb) {
    const result = rgb.match(/\d+/g); // Get all digits from rgb() string
    return "#" + result.map(x => {
        return ("0" + parseInt(x).toString(16)).slice(-2); // Convert each value to hex
    }).join('');
    }
    // [Az] Function to get the contrast color (light or dark)
    function getContrastColor(hex) {
        let r = parseInt(hex.substring(1, 3), 16);
        let g = parseInt(hex.substring(3, 5), 16);
        let b = parseInt(hex.substring(5, 7), 16);
        let brightness = (r * 299 + g * 587 + b * 114) / 1000;
        return brightness > 128 ? "#000000" : "#FFFFFF"; // Black for light, white for dark
    }

    // [Az] Update text color based on the background color
    function updateTextColorForCards() {
        const catFolders = document.querySelectorAll('.cat-folder');
        
        catFolders.forEach(folder => {
            // [Az] Get the background color (in rgb format)
            const bgColor = window.getComputedStyle(folder).backgroundColor;
            
            // [Az] Convert rgb to hex
            const hexColor = rgbToHex(bgColor);

            // [Az] Get the contrast color
            const textColor = getContrastColor(hexColor);

            // [Az] Get the <h1> element inside the folder
            const textElement = folder.querySelector('#cat-color-text');
            
            if (textElement) {
                // [Az] Apply the contrast color to the text
                textElement.style.color = textColor;
            }
        });
    }

    // [Az] Call the function after the DOM has loaded
    updateTextColorForCards();


    document.body.addEventListener("htmx:afterSwap", function () {
        setTimeout(updateTextColorForCards, 50); // Wait a bit before applying colors
    });
    

});