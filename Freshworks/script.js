document.addEventListener("DOMContentLoaded", () => {
  fetchAndDisplay("tickets", "tickets", renderTicket);
  fetchAndDisplay("contacts", "contacts", renderContact);
  fetchAndDisplay("companies", "companies", renderCompany);
  fetchAndDisplay("solutions/categories", "categories", renderCategory);
});

function fetchAndDisplay(endpoint, elementId, renderFn) {
  fetch(`${API_BASE}/${endpoint}`)
    .then(res => res.json())
    .then(data => {
      const el = document.getElementById(elementId);
      el.innerHTML = data.map(renderFn).join("");
    })
    .catch(console.error);
}

function renderTicket(t) {
  return `<li><strong>#${t.id}:</strong> ${t.subject} (Status: ${t.status})</li>`;
}
function renderContact(c) {
  return `<li>${c.name} (${c.email || "No email"})</li>`;
}
function renderCompany(c) {
  return `<li>${c.name}</li>`;
}
function renderCategory(c) {
  return `<li>${c.name}</li>`;
}

function handleSearch() {
  const type = document.getElementById("search-type").value;
  const query = document.getElementById("search-query").value;
  fetch(`${API_BASE}/search?type=${type}&query=${encodeURIComponent(query)}`)
    .then(res => res.json())
    .then(data => {
      const results = data.results || [];
      document.getElementById("search-results").innerHTML = results
        .map(item => `<li>${JSON.stringify(item)}</li>`)
        .join("");
    })
    .catch(console.error);
}
