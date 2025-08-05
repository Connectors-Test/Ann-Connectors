// js/modules/solutionCategories.js
const API_BASE = "http://localhost:3001";

export async function loadSolutionCategories(container) {
  container.innerHTML = "";

  const header = document.createElement("div");
  header.className = "flex justify-between items-center mb-4";
  header.innerHTML = `
    <h2 class="text-xl font-semibold">📚 Solution Categories</h2>
    <button id="toggle-create-category" class="bg-green-500 text-white px-3 py-1 rounded">+ Create</button>
  `;
  container.appendChild(header);

  const form = document.createElement("form");
  form.id = "create-category-form";
  form.className = "hidden bg-white p-4 rounded shadow mb-4 space-y-2";
  form.innerHTML = `
    <input type="text" name="name" placeholder="Category Name" required class="border px-2 py-1 w-full" />
    <button type="submit" class="bg-blue-500 text-white px-4 py-1 rounded">Submit</button>
  `;
  container.appendChild(form);

  document.getElementById("toggle-create-category").onclick = () => {
    form.classList.toggle("hidden");
  };

  form.onsubmit = async (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    try {
      const res = await fetch(`${API_BASE}/solutions/categories`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error("Failed to create category");
      form.reset();
      form.classList.add("hidden");
      loadSolutionCategories(container);
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  try {
    const res = await fetch(`${API_BASE}/solutions/categories`);
    const categories = await res.json();
    const list = document.createElement("ul");
    list.className = "bg-white p-4 rounded shadow space-y-2 text-sm";

    categories.forEach((c) => {
      const li = document.createElement("li");
      li.innerText = c.name;
      list.appendChild(li);
    });

    container.appendChild(list);
  } catch (err) {
    container.innerHTML += `<p class="text-red-600">Error loading categories</p>`;
  }
}
