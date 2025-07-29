const API_BASE = "http://localhost:3001";

export async function loadTickets(container) {
  container.innerHTML = "";

  const header = document.createElement("div");
  header.className = "flex justify-between items-center mb-4";
  header.innerHTML = `
    <h2 class="text-xl font-semibold">🎫 Tickets</h2>
    <button id="toggle-create-ticket" class="bg-green-500 text-white px-3 py-1 rounded">+ Create</button>
  `;
  container.appendChild(header);

  // Form (initially hidden)
  const form = document.createElement("form");
  form.id = "create-ticket-form";
  form.className = "hidden bg-white p-4 rounded shadow mb-4 space-y-2";

  form.innerHTML = `
    <input type="text" name="subject" placeholder="Subject" required class="border px-2 py-1 w-full"/>
    <textarea name="description" placeholder="Description" required class="border px-2 py-1 w-full"></textarea>
    <input type="email" name="email" placeholder="Contact Email" required class="border px-2 py-1 w-full"/>
    <button type="submit" class="bg-blue-500 text-white px-4 py-1 rounded">Submit</button>
  `;
  container.appendChild(form);

  // Toggle button
  document.getElementById("toggle-create-ticket").onclick = () => {
    form.classList.toggle("hidden");
  };

  // Submit handler
  form.onsubmit = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    try {
      const res = await fetch(`${API_BASE}/tickets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      if (!res.ok) throw new Error("Failed to create ticket");
      form.reset();
      form.classList.add("hidden");
      loadTickets(container);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  // Fetch & display existing tickets
  try {
    const res = await fetch(`${API_BASE}/tickets`);
    const tickets = await res.json();
    const list = document.createElement("ul");
    list.className = "bg-white p-4 rounded shadow space-y-2 text-sm";

    tickets.forEach(t => {
      const li = document.createElement("li");
      li.innerHTML = `<strong>#${t.id}:</strong> ${t.subject} (Status: ${t.status})`;
      list.appendChild(li);
    });

    container.appendChild(list);
  } catch (err) {
    container.innerHTML += `<p class="text-red-600">Error loading tickets</p>`;
  }
}
