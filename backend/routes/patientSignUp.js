const express = require("express");
const router = express.Router();
const path = require("path");
const bcrypt = require("bcrypt"); // Import bcrypt for password hashing

// Import the PatientSignup model
const PatientSignup = require("../models/patientSignUp");

// Define the route to serve the built React application
router.get("/signup", function (req, res, next) {
  // Serve the index.html file from the built React app
  res.sendFile(path.join(__dirname, "..", "frontend", "build", "index.html"));
});

// POST route to handle form submission
router.post("/signup", async (req, res) => {
  try {
    // Check if a user with the provided email already exists
    const existingUser = await PatientSignup.findOne({ email: req.body.email });
    if (existingUser) {
      return res.status(400).json({ message: "User already exists" });
    }

    // Hash the password
    const hashedPassword = await bcrypt.hash(req.body.password, 10); // 10 is the salt rounds

    // Create a new instance of the PatientSignup model with the hashed password
    const newPatient = new PatientSignup({
      username: req.body.username,
      email: req.body.email,
      password: hashedPassword, // Store the hashed password
    });

    // Save the new patient to the database
    await newPatient.save();

    // Send a success response
    res.status(200).json({ message: "User registered successfully" });
  } catch (error) {
    console.error("Error submitting form:", error);
    // Send an error response
    res.status(500).json({ message: "Internal Server Error" });
  }
});

module.exports = router;
