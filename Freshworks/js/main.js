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
  const type = searchType.value;
  const field = searchField.value;
  const input = document.getElementById("search-input").value.trim();
  if (!input) return;

  // Build query based on type
  const query = type === "tickets"
    ? `${field}:${input}`              // no quotes
    : `${field}:'${input}'`;          // wrap in single quotes

  try {
    const res = await fetch(`http://localhost:3001/search?type=${type}&query=${encodeURIComponent(query)}`);
    const data = await res.json();

    content.innerHTML = `
      <h2 class="text-xl font-semibold mb-2">🔍 Search Results (${type})</h2>
      <ul class="bg-white p-4 rounded shadow space-y-2 text-sm">
        ${data.results.map(r => `<li><pre class="whitespace-pre-wrap">${prettyResult(r, type)}</pre></li>`).join("")}
      </ul>
    `;
  } catch (err) {
    content.innerHTML = `<p class="text-red-600">Error loading search results</p>`;
  }
});

function prettyResult(r, type) {
  if (type === "tickets") {
    return `#${r.id} - ${r.subject} [${r.status}]`;
  } else if (type === "contacts") {
    return `${r.name} (${r.email})`;
  }
  return JSON.stringify(r, null, 2);
}

const searchField = document.getElementById("search-field");
const searchType = document.getElementById("search-type");

function updateSearchFields() {
  searchField.innerHTML = ""; // clear
  if (searchType.value === "tickets") {
    searchField.innerHTML = `<option value="status">Status</option><option value="priority">Priority</option>`;
  } else if (searchType.value === "contacts") {
    searchField.innerHTML = `<option value="email">Email</option>`;
  }
}
searchType.addEventListener("change", updateSearchFields);
updateSearchFields(); // run on load