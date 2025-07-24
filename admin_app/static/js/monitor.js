// Load full HTML before executing JS
document.addEventListener("DOMContentLoaded", function () {
    // Render a list of trips for a specific user
    function renderTrips(trips, username) {
        const tripsTable = document.querySelector("#trips_dim tbody");
        // Clear trip table placeholders
        tripsTable.innerHTML = "";

        // Check if there're no trips to show a message instead
        if (trips.length === 0) {
            tripsTable.innerHTML = `<tr><td colspan="4">No trips found.</td></tr>`;
            // Exit function early
            return;
        }

        // Loop through all trip to list details and a delete button for each row
        trips.forEach(trip => {
            // Create a new table row to display the trip name, destination, date, and a delete button with the trip id
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${trip.name}</td>
                <td>${trip.destination}</td>
                <td>${trip.date}</td>
                <td><button class="delete" data-id="${trip.id}">🗑️</button></td>
            `;

            // Select delete button to attach a listener
            const deleteBtn = row.querySelector(".delete");
            deleteBtn.addEventListener("click", () => {
                // Send a request with the username, delete action, and the trip id
                fetch(`/admin_app/monitor?username=${username}&action=delete_trip&trip_id=${trip.id}`, {
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                // Turn response to JSON data
                .then(res => res.json())

                // Name the response as updatedData and run the renderTrips function on it
                .then(updatedData => {
                    renderTrips(updatedData.trips, username);
                })
            });

            // Add the row to the trip table
            tripsTable.appendChild(row);
        });
    }

    function renderLikes(likes, username) {
        const likesTable = document.querySelector("#likes_dim tbody");
        likesTable.innerHTML = likes.length === 0 ? `<tr><td colspan="3">No likes found.</td></tr>` : "";
    
        likes.forEach(like => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${like.trip_name}</td>
                <td>${like.creator}</td>
                <td><button class="delete" data-id="${like.id}">🗑️</button></td>
            `;
            row.querySelector(".delete").addEventListener("click", () => {
                fetch(`/admin_app/monitor?username=${username}&action=delete_like&like_id=${like.id}`, {
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(res => res.json())
                .then(updatedData => renderLikes(updatedData.likes, username));
            });
            likesTable.appendChild(row);
        });
    }
    
    function renderFollowers(followers, username) {
        const table = document.querySelector("#followers_dim tbody");
        table.innerHTML = followers.length === 0 ? `<tr><td colspan="2">No followers found.</td></tr>` : "";
        
        followers.forEach(f => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${f.follower}</td>
                <td><button class="delete" data-id="${f.id}">🗑️</button></td>
            `;
            row.querySelector(".delete").addEventListener("click", () => {
                fetch(`/admin_app/monitor?username=${username}&action=delete_follower&follower_id=${f.id}`, {
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(res => res.json())
                .then(updatedData => renderFollowers(updatedData.followers, username));
            });
            table.appendChild(row);
        });
    }
    
    function renderFollowing(following, username) {
        const table = document.querySelector("#following_dim tbody");
        table.innerHTML = following.length === 0 ? `<tr><td colspan="2">Not following anyone.</td></tr>` : "";
    
        following.forEach(f => {
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${f.following}</td>
                <td><button class="delete" data-id="${f.id}">🗑️</button></td>
            `;
            row.querySelector(".delete").addEventListener("click", () => {
                fetch(`/admin_app/monitor?username=${username}&action=delete_following&following_id=${f.id}`, {
                    headers: { "X-Requested-With": "XMLHttpRequest" }
                })
                .then(res => res.json())
                .then(updatedData => renderFollowing(updatedData.following, username));
            });
            table.appendChild(row);
        });
    }

    // Select all rows to listen for clicks
    document.querySelectorAll(".user").forEach(userRow => {
        userRow.addEventListener("click", function () {
            // Grab username from clicked row
            const username = this.dataset.username;

            // Get details of the selected user using AJAX
            fetch(`/admin_app/monitor?username=${username}`, {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            })
            .then(response => response.json())
            .then(data => {
                // Display user avatar
                const avatar = document.querySelector("#mid .ava");
                if (data.pfp) {
                    avatar.src = `/media/${data.pfp}`;
                } else {
                    avatar.src = "/static/images/default-profile.png";
                }
                    
                // Display general user info
                document.querySelector("#general_details").innerHTML = `
                    <p>Name: ${data.username}</p>
                    <p>Email: ${data.email}</p>
                    <p>Staff Status: ${data.is_staff ? "Yes" : "No"}</p>
                `;

                // Display specific user info
                document.querySelector(".db4 tbody").innerHTML = `
                    <tr><td>Creation date</td><td>${data.creation_date}</td></tr>
                    <tr><td>Last active</td><td>${data.last_active_date}</td></tr>
                    <tr><td>Trips</td><td>${data.trip_amount}</td></tr>
                    <tr><td>Following</td><td>${data.following_amount}</td></tr>
                    <tr><td>Followers</td><td>${data.followers_amount}</td></tr>
                    <tr><td>Likes</td><td>${data.likes_amount}</td></tr>
                `;

                // Display account status
                document.querySelector("#status").textContent =
                    `Account status: ${data.account_status ? "Active" : "Inactive"}`;

                // Fill popup information
                renderTrips(data.trips, username);
                renderLikes(data.likes, username);
                renderFollowers(data.followers, username);
                renderFollowing(data.following, username);

                // Highlight the selected user row
                document.querySelectorAll(".user").forEach(r => r.classList.remove("selected"));
                this.classList.add("selected");
            })
        });
    });

    // Open and close popup windows using the id for the buttons and the dimmed background
    const ids = ["filter", "trips", "likes", "followers", "following"];
    ids.forEach(id => {
        const btn     = document.getElementById(id);
        const cnclBtn = document.getElementById(`${id}_cancel`);
        const popup   = document.getElementById(`${id}_dim`);

        btn.addEventListener("click", () => popup.style.display = "block");
        cnclBtn.addEventListener("click", () => popup.style.display = "none");
    });

    // Filter users based on username, email, or staff status
    document.getElementById("filter_form").addEventListener("submit", function(event) {
        // Prevent default submission refresh
        event.preventDefault();

        // Read filter inputs
        const username    = document.getElementById("username").value.toLowerCase();
        const email       = document.getElementById("email").value.toLowerCase();
        const staffStatus = document.getElementById("staff_status").checked;
        const rows        = document.querySelectorAll("tr.user");

        // Loop through users
        rows.forEach(row => {
            const rowUsername = row.dataset.username.toLowerCase();
            const rowEmail    = row.dataset.email.toLowerCase();
            const rowStaff    = row.dataset.staff === "True";

            // Check if the row matches the filter inputs
            let matches = true;
            if (username && !rowUsername.includes(username))
                matches = false;
            if (email    && !rowEmail.includes(email))
                matches = false;
            if (staffStatus && !rowStaff)
                matches = false;

            // Hide non matching rows  if matches are false by setting their display to none
            row.style.display = matches ? "" : "none";
        });

        // Close popup
        document.getElementById("filter_dim").style.display = "none";
    });
});