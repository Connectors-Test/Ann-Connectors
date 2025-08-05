// js/modules/conversations.js
const API_BASE = "http://localhost:3001";

export async function loadConversations(container) {
  container.innerHTML = "";

  const header = document.createElement("div");
  header.className = "mb-4";
  header.innerHTML = `<h2 class="text-xl font-semibold">💬 Conversations</h2>`;
  container.appendChild(header);

  const input = document.createElement("input");
  input.type = "number";
  input.placeholder = "Ticket ID";
  input.className = "border px-2 py-1 w-full mb-2";
  container.appendChild(input);

  const button = document.createElement("button");
  button.className = "bg-blue-500 text-white px-4 py-1 rounded mb-4";
  button.innerText = "Fetch";
  container.appendChild(button);

  const resultDiv = document.createElement("div");
  container.appendChild(resultDiv);

  button.onclick = async () => {
    const id = input.value;
    if (!id) return alert("Enter a ticket ID");

    resultDiv.innerHTML = "";

    try {
      const res = await fetch(`${API_BASE}/tickets/${id}/conversations`);
      const conversations = await res.json();
      const list = document.createElement("ul");
      list.className = "bg-white p-4 rounded shadow space-y-2 text-sm";

      conversations.forEach((msg) => {
        const li = document.createElement("li");
        li.innerText = `[${msg.from_email}] ${msg.body_text?.slice(0, 100)}...`;
        list.appendChild(li);
      });

      resultDiv.appendChild(list);
    } catch (err) {
      resultDiv.innerHTML = `<p class="text-red-600">Error loading conversations</p>`;
    }
  };
}
