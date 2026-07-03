async function load() {
  let list = document.getElementById("list");
  list.innerHTML =
    '<li class="list-group-item shadow-sm mb-2 rounded">Loading...</li>';

  try {
    let search = document.getElementById("search").value;
    let res = await fetch(`/appointments?search=${search}`);
    let data = await res.json();

    list.innerHTML = "";

    if (data.length === 0) {
      list.innerHTML =
        '<li class="list-group-item shadow-sm mb-2 rounded shadow-sm mb-2 rounded text-muted">No appointments yet</li>';
      return;
    }

    data.forEach((a) => {
      let badgeColor = "bg-secondary";

      if (a.status === "Confirmed") badgeColor = "bg-success";
      else if (a.status === "Cancelled") badgeColor = "bg-danger";
      else if (a.status === "Pending") badgeColor = "bg-warning";

      let li = document.createElement("li");
      li.className =
        "list-group-item shadow-sm mb-2 rounded d-flex justify-content-between align-items-center";
      li.innerHTML = `
		<div>
    		<strong>${a.name}</strong> → ${a.doctor}
    		<br>
    		<small>${a.appointment_time}</small>
            <br>
            <span class="badge ${badgeColor}">${a.status}</span>
		</div>

		<div>
    		<button class="btn btn-sm btn-warning me-2"
                onclick="editAppointment(
                ${a.id},
                '${a.name}',
                '${a.doctor}',
                '${a.appointment_time}'
                )">
                Edit
            </button>

            <button
                class="btn btn-sm btn-danger me-2"
                onclick="remove(${a.id})">
                Delete
            </button>

            <button
                class="btn btn-sm btn-success me-2"
                onclick="changeStatus(${a.id})">
                Status
            </button>

            <a
                href="/report/${a.id}"
                class="btn btn-sm btn-info">
                View Report
            </a>

		</div>
		`;
      list.appendChild(li);
    });
  } catch (e) {
    list.innerHTML =
      '<li class="list-group-item shadow-sm mb-2 rounded text-danger">Failed to load data</li>';
  }
}

async function remove(id) {
  await fetch(`/appointments/${id}`, {
    method: "DELETE",
  });

  load();
}

async function book() {
  let name = document.getElementById("name").value.trim();
  let doctor = document.getElementById("doctor").value.trim();
  let appointment_time = document.getElementById("appointment_time").value;
  let status = document.getElementById("status");

  if (!name || !doctor || !appointment_time) {
    status.innerHTML =
      '<div class="alert alert-warning">Please fill all fields</div>';
    return;
  }

  status.innerHTML = '<div class="alert alert-info">Booking...</div>';

  try {
    await fetch("/appointments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: document.getElementById("name").value,
        doctor: document.getElementById("doctor").value,
        appointment_time: document.getElementById("appointment_time").value,
        symptoms: document.getElementById("symptoms").value,
      }),
    });

    status.innerHTML =
      '<div class="alert alert-success">Appointment booked!</div>';
    document.getElementById("name").value = "";
    document.getElementById("doctor").value = "";

    load();
  } catch (e) {
    status.innerHTML =
      '<div class="alert alert-danger">Something went wrong</div>';
  }
}

async function editAppointment(id, currentName, currentDoctor, currentTime) {
  let newName = prompt("Edit name:", currentName);

  let newDoctor = prompt("Edit doctor:", currentDoctor);

  let newTime = prompt("Edit time:", currentTime);

  if (!newName || !newDoctor || !newTime) {
    return;
  }

  await fetch(`/appointments/${id}`, {
    method: "PUT",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      name: newName,
      doctor: newDoctor,
      appointment_time: newTime,
    }),
  });

  load();
}

async function saveConsultation() {
  alert("Consultation saved.");
}

async function changeStatus(id) {
  let status = prompt("Enter status:\nPending\nConfirmed\nCancelled");

  if (!status) return;

  await fetch(`/appointments/${id}/status`, {
    method: "PUT",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      status: status,
    }),
  });

  load();
}

window.onload = load;
