require("dotenv").config();
const express = require("express");
const axios = require("axios");
const app = express();
const cors = require("cors");

app.use(cors());
app.use(express.json());

// Set your Freshdesk details
const API_KEY = process.env.API_KEY;
const FRESHDESK_DOMAIN = process.env.FRESHDESK_DOMAIN;
const BASE_URL = `https://${FRESHDESK_DOMAIN}/api/v2`;
const auth = { username: API_KEY, password: "X" };

// 📇 Get all contacts
app.get("/contacts", async (req, res) => {
  const r = await axios.get(`${BASE_URL}/contacts`, { auth });
  res.json(r.data);
});

// ✅ Create contact
app.post("/contacts", async (req, res) => {
  try {
    const r = await axios.post(`${BASE_URL}/contacts`, req.body, { auth });
    res.json(r.data);
  } catch (err) {
    res.status(err.response?.status || 500).json(err.response?.data || { error: "Unknown error" });
  }
});

// 🧾 Get all tickets
app.get("/tickets", async (req, res) => {
  const r = await axios.get(`${BASE_URL}/tickets`, { auth });
  res.json(r.data);
});

// ✅ Create ticket
app.post("/tickets", async (req, res) => {
  try {
    const payload = {
      subject: req.body.subject,
      description: req.body.description,
      email: req.body.email,
      priority: 1,
      status: 2
    };

    console.log("➡️ Outgoing ticket payload:", payload);

    const r = await axios.post(`${BASE_URL}/tickets`, payload, {
      auth,
      headers: { "Content-Type": "application/json" }
    });

    res.json(r.data);
  } catch (err) {
    const errorMsg = err.response?.data || { error: "Unknown error" };
    console.error("❌ Ticket creation failed:", errorMsg);
    res.status(err.response?.status || 500).json(errorMsg);
  }
});

// 💬 Add ticket note
app.post("/tickets/:id/note", async (req, res) => {
  const ticketId = req.params.id;
  const r = await axios.post(`${BASE_URL}/tickets/${ticketId}/notes`, req.body, { auth });
  res.json(r.data);
});

// 🏢 Companies
app.get("/companies", async (req, res) => {
  const r = await axios.get(`${BASE_URL}/companies`, { auth });
  res.json(r.data);
});
app.post("/companies", async (req, res) => {
  const r = await axios.post(`${BASE_URL}/companies`, req.body, { auth });
  res.json(r.data);
});

// 📚 Solution Categories
app.get("/solutions/categories", async (req, res) => {
  const r = await axios.get(`${BASE_URL}/solutions/categories`, { auth });
  res.json(r.data);
});

// ✅ Create solution category
app.post("/solutions/categories", async (req, res) => {
  try {
    const r = await axios.post(`${BASE_URL}/solutions/categories`, req.body, { auth });
    res.json(r.data);
  } catch (err) {
    res.status(err.response?.status || 500).json(err.response?.data || { error: "Unknown error" });
  }
});

// 💬 Get conversations for a ticket
app.get("/tickets/:id/conversations", async (req, res) => {
  const ticketId = req.params.id;
  try {
    const r = await axios.get(`${BASE_URL}/tickets/${ticketId}/conversations`, { auth });
    res.json(r.data);
  } catch (err) {
    res.status(err.response?.status || 500).json(err.response?.data || { error: "Unknown error" });
  }
});

// 🔍 Search tickets or contacts
app.get("/search", async (req, res) => {
  const { type, query } = req.query;

  if (!type || !query) {
    return res.status(400).json({ error: "Missing type or query" });
  }

  console.log("➡️ SEARCH QUERY:", `${BASE_URL}/search/${type}?query=${query}`);

  try {
    const r = await axios.get(
      `${BASE_URL}/search/${type}?query="${query}"`,
      { auth }
    );
    res.json(r.data);
  } catch (err) {
    console.error("❌ Search failed:", err.response?.data || err.message);
    res.status(err.response?.status || 500).json(err.response?.data || { error: "Search failed" });
  }
});

// Server status
app.listen(3001, () => console.log("🟢 Server running on port 3001"));
