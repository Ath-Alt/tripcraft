document.addEventListener("DOMContentLoaded", function () {
    // wafa:  searsh 
    const searchInput = document.getElementById("search-input");
    const suggestionsList = document.getElementById("suggestions");
    const countries = ['Japan', 'Maldives', 'France', 'Italy', 'USA', 'Brazil', 'Australia', 'Canada'];

    if (searchInput && suggestionsList) {
        searchInput.addEventListener("input", function () {
            const query = searchInput.value.toLowerCase();
            suggestionsList.innerHTML = "";
            if (query) {
                const filtered = countries.filter(country => color.toLowerCase().startsWith(query));
                filtered.forEach(country => {
                    const li = document.createElement("li");
                    li.textContent = country;
                    li.classList.add("suggestion-item");
                    li.onclick = function () {
                        searchInput.value = country;
                        suggestionsList.innerHTML = "";
                        searchInput.form.submit();
                    };
                    suggestionsList.appendChild(li);
                });
            }
        });
    }

    // wafa:   like
    document.querySelectorAll('.like-btn').forEach(btn => {
        btn.addEventListener('click', function (event) {
            console.log('Like button clicked! Trip ID:', this.getAttribute('data-trip-id')); // wafa: logging
            event.stopPropagation(); // wafa:   click    link
            event.preventDefault();
            const tripId = this.getAttribute('data-trip-id');
            fetch('/user_app/toggle-favorite/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ trip_id: tripId })
            })
            .then(response => {
                console.log('Response status:', response.status); // wafa: logging
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data); // wafa: logging
                if (data.status === 'success') {
                    this.setAttribute('data-liked', data.action === 'liked' ? 'true' : 'false');
                    const img = this.querySelector('img');
                    if (data.action === 'liked') {
                        this.classList.add('liked');
                        img.src = '/static/images/icons/Fav-Travel.png'; // wafa:  
                    } else {
                        this.classList.remove('liked');
                        img.src = '/static/images/icons/Fav-Travel.png'; // wafa اغير الايكون:  
                    }
                    // wafa: تحديث عدد اللايكات
                    const tripCard = this.closest('.trip-card');
                    let likeCountSpan = tripCard.querySelector('.like-count');
                    if (!likeCountSpan) {
                        likeCountSpan = document.createElement('span');
                        likeCountSpan.className = 'like-count';
                        tripCard.querySelector('.card-actions').appendChild(likeCountSpan);
                    }
                    likeCountSpan.textContent = `${data.likes_count} Likes`;
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error); // wafa: logging
                alert('An error occurred while processing your request.');
            });
        });
    });

    // wafa:   following
    document.querySelectorAll('.follow-btn').forEach(btn => {
        btn.addEventListener('click', function (event) {
            console.log('Follow button clicked! Follow ID:', this.getAttribute('data-follow-id')); // wafa: logging
            event.stopPropagation(); // wafa:   click    link
            event.preventDefault();
            const followId = this.getAttribute('data-follow-id');
            fetch('/user_app/toggle-follow/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                },
                body: JSON.stringify({ follow_id: followId })
            })
            .then(response => {
                console.log('Response status:', response.status); // wafa: logging
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data); // wafa: logging
                if (data.status === 'success') {
                    this.setAttribute('data-following', data.action === 'followed' ? 'true' : 'false');
                    const img = this.querySelector('img');
                    if (data.action === 'followed') {
                        this.classList.add('followed');
                        img.src = '/static/images/icons/follow.png'; // wafa: أيقونة متابعة
                    } else {
                        this.classList.remove('followed');
                        img.src = '/static/images/icons/follow.png'; // wafa:  اغير الايكون 
                    }
                } else {
                    alert('Error: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error); // wafa: logging
                alert('An error occurred while processing your request.');
            });
        });
    });

    // wafa:  CSRF and logging
    function getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        console.log('CSRF Token:', cookieValue); // wafa: logging
        return cookieValue;
    }
});