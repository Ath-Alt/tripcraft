
     // Close Popup on Cancel Button Click
     document.addEventListener('DOMContentLoaded', () => {
        const settingsBtn = document.getElementById("settings");
        const settingsCancelBtn = document.getElementById("settings_cancel");
        const settingsPopup = document.getElementById("settings_dim");
        const saveSettingsBtn = document.getElementById("saveSettings");
            
        settingsBtn.addEventListener("click", function() {
            settingsPopup.style.display = "flex";
        });
        
        settingsCancelBtn.addEventListener("click", function() {
            settingsPopup.style.display = "none";
        });

        saveSettingsBtn.addEventListener("click", function() {
            // Get values from the input fields
            const avatar = document.getElementById('photoUpload').files[0]; // Get the file for avatar
            const username = document.getElementById('username').value;  // Get the username input value
            const email = document.getElementById('email').value;        // Get the email input value
            const bio = document.getElementById('userBio').value;        // Get the bio input value
            const password = document.getElementById('password').value;  // Get the password input value
    
            // Call the updateSettings function
            updateSettings(avatar, username, email, bio, password);
        });

        function updateSettings(avatar, username, email, bio, password) {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('email', email);
            formData.append('bio', bio);
            formData.append('password', password);
        
            // Check if avatar is selected
            if (avatar) {
                formData.append('avatar', avatar);
            }
        
            // Add CSRF token
            formData.append('csrfmiddlewaretoken', '{{ csrf_token }}');
        
            $.ajax({
                url: '/settings/',  // URL to send the request
                type: 'POST',       // POST request
                data: formData,     // Form data
                processData: false, // Don't process data (important for file uploads)
                contentType: false, // Let jQuery determine the content type (important for FormData)
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("X-CSRFToken", '{{ csrf_token }}');
                },
                success: function(data) {
                    console.log('Response data:', data);
        
                    // Show success message (optional)
                    const messageContainer = $('#messages');
                    if (data.status === 'success') {
                        messageContainer.html('<div class="alert alert-success">' + data.message + '</div>');
                    } else {
                        messageContainer.html('<div class="alert alert-danger">' + data.message + '</div>');
                    }
        
                    // Update the username dynamically
                    if (data.new_username) {
                        $('#username-display').text(data.new_username);  // Target the h3 with id="username"
                    }

                    // Update the avatar dynamically
                    if (data.new_avatar_url) {
                        $('img.ava').attr('src', data.new_avatar_url);  // Target the img with class="ava"
                    }
        
                    // Optionally remove the success/error message after 5 seconds
                    setTimeout(function() {
                        messageContainer.html('');
                    }, 5000);  // 5000ms = 5 seconds
                },
                error: function(xhr, status, error) {
                    console.error('Error:', error);
                    $('#messages').html('<div class="alert alert-danger">Failed to update settings.</div>');
                }
            });
        }
        const likesSwitch = document.getElementById('likesNotifications');
        const followersSwitch = document.getElementById('followersNotifications');
    
        likesSwitch.addEventListener('change', function() {
            updateNotificationSetting('likes_notifications', likesSwitch.checked);
        });
    
        followersSwitch.addEventListener('change', function() {
            updateNotificationSetting('followers_notifications', followersSwitch.checked);
        });
    
        // Function to update NOTIFICATION settings
        function updateNotificationSetting(settingName, settingValue) {
            $.ajax({
                url: '/settings/',
                type: 'POST',
                data: {
                    name: 'notification_setting',
                    setting: settingName,
                    value: settingValue,
                    csrfmiddlewaretoken: '{{ csrf_token }}'
                },
                success: function(response) {
                    console.log(response);
                    if (response.status === 'success') {
                        console.log('Notification setting updated');
                    } else {
                        console.error('Failed to update notification setting:', response.message);
                    }
                },
                error: function(xhr, errmsg, err) {
                    console.error("Error:", errmsg);
                }
            });
        }
});
