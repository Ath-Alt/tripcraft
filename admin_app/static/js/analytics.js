// Wait till HTML is loaded
document.addEventListener("DOMContentLoaded", function () {
    // Get canvases by id
    var ctx1 = document.getElementById('userActivity').getContext('2d');
    var ctx2 = document.getElementById('featureUsage').getContext('2d');
    var ctx3 = document.getElementById('engagementType').getContext('2d');
    var ctx4 = document.getElementById('genderCount').getContext('2d');

    // User activity line graph
    var userActivityChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: activity_dates,
            datasets: [{
                label: 'User Activity',
                data: activity_counts,
                backgroundColor: '#428EFF90',
                borderColor: '#428EFF',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 20,
                    right: 50,
                    top: 20,
                    bottom: 20
                }
            }
        }
    })

    // Feature usage bar graph
    var featureUsageChart = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: feature_names,
            datasets: [{
                label: 'Feature Usage',
                data: feature_clicks,
                backgroundColor: '#9542FF90',
                borderColor: '#9542FF',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    })

    // Engagement type doughtnut chart
    var engagementTypeChart = new Chart(ctx3, {
        type: 'doughnut',
        data: {
            labels: ['Follow', 'Like'],
            datasets: [{
                label: 'Engagement Type',
                data: [follow_count, like_count],
                backgroundColor: ['#9542FFCC', '#FFB342CC'],
                borderColor: ['#8A2DFF', '#FF8C00'],
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false
        }
    })

    // Gender distribution pie chart
    var genderCountChart = new Chart(ctx4, {
        type: 'pie',
        data: {
            labels: ['Female', 'Male'],
            datasets: [{
                label: 'Gender Distribution',
                data: [female_count, male_count],
                backgroundColor: ['#FF5D80CC', '#428EFFCC'],
                borderColor: ['#E14D6A', '#1E66CC'],
                borderWidth: 3,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: false,
            maintainAspectRatio: false
        }
    })
})