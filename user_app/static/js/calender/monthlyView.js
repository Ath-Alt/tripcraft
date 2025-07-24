document.addEventListener("DOMContentLoaded", function () {
    var calendarEl = document.getElementById("calendarM");

    if (!calendarEl) {
        console.error("Calendar div is missing!");
        return;
    }

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: "dayGridMonth",
        contentHeight: "auto", 
        windowResize: function(view) {
            calendar.updateSize(); // Update size on window resize
        },
        events: function(info, successCallback, failureCallback) {
            fetch('/get_trips_for_calendar/')
                .then(response => response.json())
                .then(data => successCallback(data))
                .catch(error => failureCallback(error));
        },
    });

    calendar.render();

    //[Az] Extra safeguard: trigger size update on window resize
    window.addEventListener("resize", function () {
        calendar.updateSize();
    });
});
