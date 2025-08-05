// js/modules/companies.js
const API_BASE = "http://localhost:3001";

export async function loadCompanies(container) {
  container.innerHTML = "";

  const header = document.createElement("div");
  header.className = "flex justify-between items-center mb-4";
  header.innerHTML = `
    <h2 class="text-xl font-semibold">🏢 Companies</h2>
    <button id="toggle-create-company" class="bg-green-500 text-white px-3 py-1 rounded">+ Create</button>
  `;
  container.appendChild(header);

  const form = document.createElement("form");
  form.id = "create-company-form";
  form.className = "hidden bg-white p-4 rounded shadow mb-4 space-y-2";
  form.innerHTML = `
    <input type="text" name="name" placeholder="Company Name" required class="border px-2 py-1 w-full" />
    <button type="submit" class="bg-blue-500 text-white px-4 py-1 rounded">Submit</button>
  `;
  container.appendChild(form);

  document.getElementById("toggle-create-company").onclick = () => {
    form.classList.toggle("hidden");
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    try {
      const res = await fetch(`${API_BASE}/companies`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to create company");
      form.reset();
      form.classList.add("hidden");
      loadCompanies(container);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  try {
    const res = await fetch(`${API_BASE}/companies`);
    const companies = await res.json();
    const list = document.createElement("ul");
    list.className = "bg-white p-4 rounded shadow space-y-2 text-sm";

    companies.forEach((c) => {
      const li = document.createElement("li");
      li.innerText = c.name;
      list.appendChild(li);
    });

    container.appendChild(list);
  } catch (err) {
    container.innerHTML += `<p class="text-red-600">Error loading companies</p>`;
  }
}
