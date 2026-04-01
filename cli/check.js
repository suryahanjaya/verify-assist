#!/usr/bin/env node

/**
 * VerifyAssist CLI
 *
 * Pipeline: ESLint → extract warnings → send to /verify API → display results
 *
 * Usage:
 *   node check.js                    # lint example.js (default)
 *   node check.js src/app.js         # lint a specific file
 */

const { exec } = require("child_process");
const fs = require("fs");
const path = require("path");
const axios = require("axios");

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------
const API_URL = process.env.VERIFYASSIST_URL || "http://localhost:8000/verify";
const CONTEXT_LINES = 10; // lines above/below the warning to include
const TARGET_FILE = process.argv[2] || "example.js";

// ---------------------------------------------------------------------------
// Terminal colours (ANSI)
// ---------------------------------------------------------------------------
const CLR = {
  reset: "\x1b[0m",
  bold: "\x1b[1m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  magenta: "\x1b[35m",
  cyan: "\x1b[36m",
  white: "\x1b[37m",
  bgRed: "\x1b[41m",
  bgGreen: "\x1b[42m",
  bgYellow: "\x1b[43m",
};

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/**
 * Read a file and extract ±CONTEXT_LINES around a target line number.
 */
function extractContext(filePath, lineNumber) {
  try {
    const content = fs.readFileSync(filePath, "utf-8");
    const lines = content.split("\n");

    const start = Math.max(0, lineNumber - CONTEXT_LINES - 1);
    const end = Math.min(lines.length, lineNumber + CONTEXT_LINES);

    const snippet = lines
      .slice(start, end)
      .map((line, i) => {
        const num = start + i + 1;
        const marker = num === lineNumber ? " ►" : "  ";
        return `${marker} ${String(num).padStart(4)} │ ${line}`;
      })
      .join("\n");

    return snippet;
  } catch (err) {
    return `[Could not read file: ${err.message}]`;
  }
}

/**
 * Run ESLint on the target file and return parsed JSON results.
 */
function runEslint(filePath) {
  return new Promise((resolve, reject) => {
    const absPath = path.resolve(filePath);

    if (!fs.existsSync(absPath)) {
      return reject(new Error(`File not found: ${absPath}`));
    }

    const cmd = `npx eslint "${absPath}" -f json`;

    exec(cmd, { cwd: __dirname, maxBuffer: 1024 * 1024 }, (error, stdout) => {
      // ESLint exits with code 1 when it finds warnings — that's expected
      if (error && !stdout) {
        return reject(
          new Error(
            `ESLint execution failed.\n` +
              `Make sure ESLint is installed: npm install\n\n` +
              `Details: ${error.message}`
          )
        );
      }

      try {
        const results = JSON.parse(stdout);
        resolve(results);
      } catch (parseErr) {
        reject(new Error(`Failed to parse ESLint JSON output: ${parseErr.message}`));
      }
    });
  });
}

/**
 * Send a single warning to the VerifyAssist backend.
 */
async function verifyWarning(warning, codeSnippet, filePath) {
  const payload = {
    warning_message: warning.message,
    category: warning.ruleId || "unknown",
    code_snippet: codeSnippet,
    optional_context: `File: ${filePath}, Line: ${warning.line}, Severity: ${
      warning.severity === 2 ? "error" : "warning"
    }`,
  };

  const response = await axios.post(API_URL, payload, {
    headers: { "Content-Type": "application/json" },
    timeout: 30000,
  });

  return response.data;
}

/**
 * Map classification to coloured label.
 */
function classificationLabel(cls) {
  switch (cls) {
    case "TRUE_POSITIVE":
      return `${CLR.bgRed}${CLR.white}${CLR.bold} TRUE_POSITIVE ${CLR.reset}`;
    case "FALSE_POSITIVE":
      return `${CLR.bgGreen}${CLR.white}${CLR.bold} FALSE_POSITIVE ${CLR.reset}`;
    case "TOLERABLE":
      return `${CLR.bgYellow}${CLR.white}${CLR.bold} TOLERABLE ${CLR.reset}`;
    default:
      return cls;
  }
}

/**
 * Format confidence as a visual bar.
 */
function confidenceBar(value) {
  const pct = Math.round(value * 100);
  const filled = Math.round(value * 20);
  const bar = "█".repeat(filled) + "░".repeat(20 - filled);
  let colour = CLR.green;
  if (pct < 60) colour = CLR.red;
  else if (pct < 80) colour = CLR.yellow;
  return `${colour}${bar}${CLR.reset} ${CLR.bold}${pct}%${CLR.reset}`;
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  console.log();
  console.log(
    `${CLR.bold}${CLR.cyan}╔══════════════════════════════════════════════════╗${CLR.reset}`
  );
  console.log(
    `${CLR.bold}${CLR.cyan}║         VerifyAssist  ·  ESLint → LLM           ║${CLR.reset}`
  );
  console.log(
    `${CLR.bold}${CLR.cyan}╚══════════════════════════════════════════════════╝${CLR.reset}`
  );
  console.log();
  console.log(`${CLR.dim}Target file : ${CLR.reset}${CLR.bold}${TARGET_FILE}${CLR.reset}`);
  console.log(`${CLR.dim}Backend API : ${CLR.reset}${CLR.bold}${API_URL}${CLR.reset}`);
  console.log();

  // --- 1. Run ESLint -------------------------------------------------------
  console.log(`${CLR.cyan}[1/3]${CLR.reset} Running ESLint …`);

  let eslintResults;
  try {
    eslintResults = await runEslint(TARGET_FILE);
  } catch (err) {
    console.error(`${CLR.red}✖ ESLint error:${CLR.reset} ${err.message}`);
    process.exit(1);
  }

  // --- 2. Collect warnings --------------------------------------------------
  const fileResult = eslintResults[0];
  if (!fileResult || !fileResult.messages || fileResult.messages.length === 0) {
    console.log(`${CLR.green}✔ No warnings found. File is clean!${CLR.reset}`);
    process.exit(0);
  }

  const warnings = fileResult.messages;
  const filePath = fileResult.filePath;

  console.log(
    `${CLR.cyan}[2/3]${CLR.reset} Found ${CLR.bold}${warnings.length}${CLR.reset} warning(s)\n`
  );

  // --- 3. Verify each warning -----------------------------------------------
  console.log(
    `${CLR.cyan}[3/3]${CLR.reset} Sending to VerifyAssist backend …\n`
  );

  const separator = `${CLR.dim}${"─".repeat(60)}${CLR.reset}`;
  let truePos = 0;
  let falsePos = 0;
  let tolerable = 0;
  let failed = 0;

  for (let i = 0; i < warnings.length; i++) {
    const w = warnings[i];
    const idx = `[${i + 1}/${warnings.length}]`;

    console.log(separator);
    console.log(
      `${CLR.bold}${CLR.magenta}${idx}${CLR.reset}  ` +
        `${CLR.bold}Line ${w.line}${CLR.reset}  ` +
        `${CLR.yellow}${w.ruleId || "unknown"}${CLR.reset}`
    );
    console.log(`${CLR.dim}    "${w.message}"${CLR.reset}`);
    console.log();

    // Extract code context
    const snippet = extractContext(filePath, w.line);

    // Send to backend
    try {
      const result = await verifyWarning(w, snippet, filePath);

      // Tally
      if (result.classification === "TRUE_POSITIVE") truePos++;
      else if (result.classification === "FALSE_POSITIVE") falsePos++;
      else tolerable++;

      // Display
      console.log(
        `    ${CLR.bold}Verdict :${CLR.reset} ${classificationLabel(result.classification)}`
      );
      console.log(`    ${CLR.bold}Confidence :${CLR.reset} ${confidenceBar(result.confidence)}`);
      console.log(`    ${CLR.bold}Explanation:${CLR.reset} ${result.explanation}`);
      console.log(`    ${CLR.bold}Evidence   :${CLR.reset} ${CLR.dim}${result.evidence}${CLR.reset}`);

      if (result.cached) {
        console.log(`    ${CLR.dim}(served from cache)${CLR.reset}`);
      }
    } catch (err) {
      failed++;
      if (err.response) {
        console.log(
          `    ${CLR.red}✖ API error ${err.response.status}:${CLR.reset} ${
            err.response.data?.detail || err.message
          }`
        );
      } else if (err.code === "ECONNREFUSED") {
        console.log(
          `    ${CLR.red}✖ Cannot reach backend at ${API_URL}${CLR.reset}`
        );
        console.log(
          `    ${CLR.dim}  Make sure the server is running: cd ../backend && uvicorn app.main:app --reload${CLR.reset}`
        );
      } else {
        console.log(`    ${CLR.red}✖ Error: ${err.message}${CLR.reset}`);
      }
    }

    console.log();
  }

  // --- Summary --------------------------------------------------------------
  console.log(separator);
  console.log();
  console.log(`${CLR.bold}${CLR.cyan}Summary${CLR.reset}`);
  console.log(
    `  Total warnings  : ${CLR.bold}${warnings.length}${CLR.reset}`
  );
  console.log(
    `  ${CLR.red}■${CLR.reset} True Positive  : ${CLR.bold}${truePos}${CLR.reset}`
  );
  console.log(
    `  ${CLR.green}■${CLR.reset} False Positive : ${CLR.bold}${falsePos}${CLR.reset}`
  );
  console.log(
    `  ${CLR.yellow}■${CLR.reset} Tolerable      : ${CLR.bold}${tolerable}${CLR.reset}`
  );
  if (failed > 0) {
    console.log(
      `  ${CLR.red}■${CLR.reset} Failed         : ${CLR.bold}${failed}${CLR.reset}`
    );
  }
  console.log();
}

// ---------------------------------------------------------------------------
main().catch((err) => {
  console.error(`${CLR.red}Fatal error:${CLR.reset}`, err.message);
  process.exit(1);
});
