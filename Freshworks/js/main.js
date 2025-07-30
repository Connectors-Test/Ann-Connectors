import { loadTickets } from "./modules/tickets.js";
import { loadContacts } from "./modules/contacts.js";
import { loadCompanies } from "./modules/companies.js";
import { loadSolutionCategories } from "./modules/solutions.js";
import { loadConversations } from "./modules/conversations.js";

const content = document.getElementById("content-area");

const routes = {
  tickets: loadTickets,
  contacts: loadContacts,
  companies: loadCompanies,
  categories: loadSolutionCategories,
  conversations: loadConversations
};

document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const page = btn.getAttribute("data-page");
    if (routes[page]) routes[page](content);
  });
});

// Default route
routes["tickets"](content);

// Search logic
document.getElementById("search-btn").addEventListener("click", async () => {
  const type = document.getElementById("search-type").value;
  const query = document.getElementById("search-input").value;
  if (!query) return;

  try {
    const res = await fetch(`http://localhost:3001/search?type=${type}&query=${encodeURIComponent(query)}`);
    const data = await res.json();

    content.innerHTML = `
      <h2 class="text-xl font-semibold mb-2">🔍 Search Results (${type})</h2>
      <ul class="bg-white p-4 rounded shadow space-y-2 text-sm">
        ${data.results.map(r => `<li>${JSON.stringify(r)}</li>`).join("")}
      </ul>
    `;
  } catch (err) {
    content.innerHTML = `<p class="text-red-600">Error loading search results</p>`;
  }
});
