document.addEventListener('DOMContentLoaded', function () {

  let currentDay = 0; // 0 = Day 1
  
  const calendarEl = document.getElementById('calendar');
  const tripId = calendarEl.dataset.tripId;
  const maxDays = parseInt(calendarEl.dataset.duration);  // now dynamic
  const fallbackDate = '2025-01-01'; // just a fixed starting point
  const startDateRaw = calendarEl.dataset.startDate;
  const tripStartDate = startDateRaw ? new Date(startDateRaw) : new Date(fallbackDate);
  const hasDates = calendarEl.dataset.hasDates === "true";



  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'timeGridDay',
    editable: true,
    selectable: true,
    allDaySlot: false,
    droppable: true,
    slotMinTime: "06:00:00",
    slotMaxTime: "22:00:00",
    slotDuration: "00:30:00",
    headerToolbar: false,
    events: `/api/daily-events/${tripId}`, // [Az] tripId is Django Trip ID (fetch from backend)
    

    dayHeaders: true,
    dayHeaderContent: function (args) {
      return hasDates ? args.text : '';
    },
    eventDrop: function (info) {
      updateEventTime(info.event);
    },
    eventResize: function (info) {
      updateEventTime(info.event);
    },

    select: function (info) {
      openModal(info.start, info.end); // Pre-fill modal with selected times
    },
    eventClick: function (info) {
      // Edit existing event
      const event = info.event;
      openModal(event.start, event.end, event);
    },

    eventDidMount: function(info) {
      console.log("Rendering event:", info.event.title, info.event.start, info.event.end);
    }
    
    
  });

  calendar.render();

  // [Az] Force initial view to simulated Day 1
  const initialDate = new Date(tripStartDate);
  calendar.gotoDate(initialDate);
  const viewDate = new Date(tripStartDate);
  viewDate.setDate(tripStartDate.getDate() + currentDay);
  calendar.gotoDate(viewDate);

  // [Az]  Utility to convert Date to local HH:MM format
  function toTimeStringLocal(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
  }

  function updateDayLabel() {
    const label = hasDates
      ? calendar.view.currentStart.toLocaleDateString('en-US', {
          month: 'short',
          day: 'numeric'
        })
      : `Day ${currentDay + 1}`;
  
    document.getElementById("dayLabel").textContent = label;
  }
  updateDayLabel();

  // Prev button
  document.getElementById("prevBtn").addEventListener("click", () => {
    if (currentDay > 0) {
      currentDay--;
      const prevDate = new Date(tripStartDate);
      prevDate.setDate(tripStartDate.getDate() + currentDay);
      calendar.gotoDate(prevDate);
      updateDayLabel();
    }
  });

  // Next button
  document.getElementById("nextBtn").addEventListener("click", () => {
    if (currentDay < maxDays - 1) {
      currentDay++;
      const nextDate = new Date(tripStartDate);
      nextDate.setDate(tripStartDate.getDate() + currentDay);
      calendar.gotoDate(nextDate);
      updateDayLabel();
    }
  });

  // Manual "Add Event" button
  document.getElementById("addEventBtn").addEventListener("click", () => {
    openModal(); // No pre-filled time
  });

  // [Az] Open the modal and optionally fill in start/end times

  function openModal(start = '', end = '', event = null) {
    const modal = document.getElementById("eventModal");
    modal.style.display = "block";

    // [Az] Fill form fields
    document.querySelector("#eventForm input[name='start_time']").value =
      start ? toTimeStringLocal(start) : '';
    document.querySelector("#eventForm input[name='end_time']").value =
      end ? toTimeStringLocal(end) : '';

    document.querySelector("#eventForm input[name='name']").value = event ? event.title : '';
    document.querySelector("#eventForm input[name='location']").value = event?.extendedProps?.location || '';
    document.querySelector("#eventForm textarea[name='description']").value = event?.extendedProps?.description || '';
    document.querySelector("#eventForm input[name='event_id']").value = event?.id || '';

    
    // [Az] Show or hide delete button
    const deleteBtn = document.getElementById("deleteEventButton");
    if (event) {
      deleteBtn.style.display = "inline-block"; // show in edit mode
      deleteBtn.dataset.eventId = event.id;     // store event ID
    } else {
      deleteBtn.style.display = "none"; // hide in add mode
      deleteBtn.removeAttribute("data-event-id");
    }
  }

  // [Az] Close the modal
  document.getElementById("closeModal").addEventListener("click", () => {
    document.getElementById("eventModal").style.display = "none";
    document.getElementById("eventForm").reset();
  });

  // [Az] Handle event creation from form
  document.getElementById("eventForm").addEventListener("submit", function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    const name = formData.get("name");
    const location = formData.get("location");
    const description = formData.get("description");
    const startTime = formData.get("start_time");
    const endTime = formData.get("end_time");
    const eventId = formData.get("event_id");
    const day_number = currentDay + 1;

    const eventDate = new Date(tripStartDate);
    eventDate.setDate(tripStartDate.getDate() + currentDay);

    const yyyy = eventDate.getFullYear();
    const mm = String(eventDate.getMonth() + 1).padStart(2, '0');
    const dd = String(eventDate.getDate()).padStart(2, '0');
    const formattedDate = `${yyyy}-${mm}-${dd}`;

    const eventData = {
      name,
      location,
      description,
      day_number,
      start_time: startTime,
      end_time: endTime
    };

    const url = eventId
      ? `/api/edit-event/${eventId}/`
      : `/api/create-event/${tripId}/`;

    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
      },
      body: JSON.stringify(eventData)
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        const fullStart = `${formattedDate}T${startTime}`;
        const fullEnd = `${formattedDate}T${endTime}`;

        if (eventId) {
          const event = calendar.getEventById(eventId);
          if (event) {
            event.setProp('title', name);
            event.setStart(fullStart);
            event.setEnd(fullEnd);
          }
        } else {
          calendar.addEvent({
            title: `${name} (Day ${day_number})`,
            start: fullStart,
            end: fullEnd,
            id: data.id,
            color: "#4CAF50"
          });
        }

        this.reset();
        document.getElementById("eventModal").style.display = "none";
      } else {
        alert("Failed to save event: " + data.message);
      }
    });
  });
  // [Az] for deleting events 
  document.getElementById("deleteEventButton").addEventListener("click", function () {
    const eventId = this.dataset.eventId;
    if (!eventId) return;
  
    const confirmed = confirm("Are you sure you want to delete this event?");
    if (!confirmed) return;
  
    fetch(`/api/delete-event/${eventId}/`, {
      method: "POST",  
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === "success") {
        // Remove from calendar
        const event = calendar.getEventById(eventId);
        if (event) event.remove();
  
        // Close modal and reset form
        document.getElementById("eventModal").style.display = "none";
        document.getElementById("eventForm").reset();
      } else {
        alert("Failed to delete event: " + data.message);
      }
    });
  });


  function updateEventTime(event) {
    fetch(`/api/update-event-time/${event.id}/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie('csrftoken')  // optional if using CSRF
      },
      body: JSON.stringify({
        start: event.start.toISOString(),
        end: event.end.toISOString()
      })
    })
    .then(response => response.json())
    .then(data => {
      if (data.status !== "success") {
        alert("Failed to update event time: " + data.message);
      }
    });
  }
  // [Az] for cookies 
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(cookie.slice(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  
  
});
