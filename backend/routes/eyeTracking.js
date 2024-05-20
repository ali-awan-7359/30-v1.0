const express = require("express");
const router = express.Router();
const { exec, spawn } = require("child_process");
const path = require("path");

const scriptPath = path.join(__dirname, "..", "extract.py");
let scriptProcess = null;

router.post("/start-eye-tracking", (req, res) => {
  if (scriptProcess) {
    return res
      .status(400)
      .json({ message: "Eye tracking script is already running" });
  }

  const command = `python "${scriptPath}"`;
  console.log(`Executing command: ${command}`);

  scriptProcess = spawn("python", [scriptPath]);

  scriptProcess.stdout.on("data", (data) => {
    console.log(`Script output: ${data}`);
  });

  scriptProcess.stderr.on("data", (data) => {
    console.error(`Script error: ${data}`);
  });

  scriptProcess.on("close", (code) => {
    console.log(`Script exited with code ${code}`);
    scriptProcess = null;
  });

  res.status(200).json({ message: "Eye tracking started successfully" });
});

router.post("/stop-eye-tracking", (req, res) => {
  if (!scriptProcess) {
    return res
      .status(400)
      .json({ message: "No eye tracking script is running" });
  }

  scriptProcess.stdin.write("q\n");
  scriptProcess.kill("SIGINT");
  scriptProcess = null;

  res.status(200).json({ message: "Eye tracking stopped successfully" });
});

module.exports = router;
