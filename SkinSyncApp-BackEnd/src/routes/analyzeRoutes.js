const express = require("express");
const { analyzeSkin } = require("../controllers/analyzeController");
const router = express.Router();

router.post("/analyze", analyzeSkin);

module.exports = router;
