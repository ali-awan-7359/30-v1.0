// backend/routes/login.js

const express = require("express");
const router = express.Router();
const bcrypt = require("bcrypt");
const PatientSignUp = require("../models/patientSignUp");

router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  try {
    console.log("Email:", email); // Log email received from frontend
    console.log("Password:", password); // Log password received from frontend

    // Check if the user exists in the database
    const user = await PatientSignUp.findOne({ email }).select(
      "+password email"
    );

    console.log("User:", user); // Log user retrieved from database

    if (!user) {
      console.log("User not found");
      return res.status(400).json({ message: "Invalid email or password" });
    }

    // Compare passwords
    let isPasswordValid;
    if (await bcrypt.compare(password, user.password)) {
      // If the entered password matches the hashed password in the database
      isPasswordValid = true;
    } else if (password === user.password) {
      // If the entered password matches the non-hashed password in the database
      isPasswordValid = true;
    } else {
      // If neither hashed nor non-hashed password matches
      isPasswordValid = false;
    }

    if (!isPasswordValid) {
      console.log("Invalid password");
      return res.status(400).json({ message: "Invalid email or password" });
    }

    // User authenticated successfully
    console.log("Login successful");
    return res.status(200).json({ message: "Login successful" });
  } catch (error) {
    console.error("Error logging in:", error);
    return res.status(500).json({ message: "Internal Server Error" });
  }
});

module.exports = router;
