require("dotenv").config();
const express = require("express");
const cors = require("cors");

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" }));

// Routes
const authRoutes = require("./routes/authRoutes");
const analyzeRoutes = require("./routes/analyzeRoutes");
app.use("/api/auth", authRoutes);
app.use("/api", analyzeRoutes);

app.get("/", (req, res) => {
  res.send("SkinSync API is running!");
});

// Jalankan server
app.listen(port, () => {
  console.log(`Server is listening on http://localhost:${port}`);
});
