document.addEventListener('DOMContentLoaded', () => {
    console.log('Favorites page loaded');
    const cards = document.querySelectorAll('.trip-card');
    console.log(`Number of trip cards: ${cards.length}`);
    document.body.addEventListener('htmx:afterRequest', (event) => {
        if (event.detail.successful) {
            console.log('Favorite toggled successfully');
        } else {
            console.error('Error toggling favorite:', event.detail.xhr.statusText);
            alert('Failed to update favorite. Please try again.');
        }
    });
});