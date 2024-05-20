const express = require("express");
const router = express.Router();
const path = require("path");
const xlsx = require("xlsx");

// Route to get eye tracking data
router.get("/data", (req, res) => {
  const filePath = path.join(__dirname, "..", "eye_coordinates.xlsx");

  try {
    const workbook = xlsx.readFile(filePath);
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const data = xlsx.utils.sheet_to_json(sheet);

    res.status(200).json(data);
  } catch (error) {
    console.error("Error reading Excel file:", error);
    res.status(500).json({ message: "Error reading Excel file" });
  }
});

module.exports = router;
