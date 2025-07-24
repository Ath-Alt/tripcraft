// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const bellBtn = document.querySelector('.bell-btn');
    const dropdown = document.getElementById('notification-dropdown');
    if (!bellBtn.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});
function filterFollowing() {
    const searchBar = document.getElementById('searchBar');
    const filter = searchBar.value.toLowerCase();
    const following = document.getElementsByClassName('follow-card');

    for (let i = 0; i < following.length; i++) {
        const username = following[i].getAttribute('data-username').toLowerCase();
        if (username.includes(filter)) {
            following[i].style.display = '';
        } else {
            following[i].style.display = 'none';
        }
    }
}

function deleteFollow(button) {
    const card = button.parentElement.parentElement;
    card.remove();
}

// Toggle notifications dropdown
function toggleNotifications() {
    const dropdown = document.getElementById('notification-dropdown');
    dropdown.classList.toggle('show');
}

// Toggle favorite button
function toggleFavorite(button) {
    button.classList.toggle('active');
}

// Close dropdown when clicking outside
document.addEventListener('click', function(event) {
    const bellBtn = document.querySelector('.bell-btn');
    const dropdown = document.getElementById('notification-dropdown');
    if (!bellBtn.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.classList.remove('show');
    }
});