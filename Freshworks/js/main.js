import { loadTickets } from "./modules/tickets.js";
// import { loadContacts } from "./modules/contacts.js"; // next

const content = document.getElementById("content-area");

const routes = {
  tickets: loadTickets,
  contacts: () => content.innerHTML = "TODO: Contacts",
  companies: () => content.innerHTML = "TODO: Companies",
  categories: () => content.innerHTML = "TODO: Categories",
};

document.querySelectorAll(".nav-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const page = btn.getAttribute("data-page");
    if (routes[page]) routes[page](content);
  });
});

// Default route
routes["tickets"](content);

// Search will be implemented after all base modules are done
