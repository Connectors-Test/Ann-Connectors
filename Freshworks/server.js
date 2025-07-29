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

// 🧾 Get all tickets
app.get("/tickets", async (req, res) => {
  const r = await axios.get(`${BASE_URL}/tickets`, { auth });
  res.json(r.data);
});

// ✅ Create ticket
app.post("/tickets", async (req, res) => {
  const r = await axios.post(`${BASE_URL}/tickets`, req.body, { auth });
  res.json(r.data);
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

// 🔍 Search tickets or contacts
app.get("/search", async (req, res) => {
  const { type, query } = req.query;

  if (!type || !query) {
    return res.status(400).json({ error: "Missing type or query" });
  }

  const r = await axios.get(
    `${BASE_URL}/search/${type}?query="${query}"`,
    { auth }
  );
  res.json(r.data);
});

// Server status
app.listen(3001, () => console.log("🟢 Server running on port 3001"));
