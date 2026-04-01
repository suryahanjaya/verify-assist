/**
 * Example file with intentional static analysis warnings.
 * Used to demonstrate the VerifyAssist CLI pipeline.
 */

const express = require("express");

// WARNING 1: no-unused-vars — 'config' is declared but never used
const config = {
  port: 3000,
  host: "localhost",
  debug: true,
};

// WARNING 2: no-unused-vars — 'helperUtil' is never used
const helperUtil = require("./utils/helper");

function processUserData(user) {
  // WARNING 3: eqeqeq — using == instead of ===
  if (user.role == "admin") {
    console.log("Admin access granted for:", user.name);
  }

  // WARNING 4: no-constant-condition — condition is always true
  if (true) {
    console.log("This block always executes");
  }

  // WARNING 5: no-empty — empty catch block
  try {
    const data = JSON.parse(user.payload);
    return data;
  } catch (e) {}

  return null;
}

function calculateDiscount(price, tier) {
  let discount;

  switch (tier) {
    case "gold":
      discount = price * 0.3;
    // WARNING 6: no-fallthrough — missing break before next case
    case "silver":
      discount = price * 0.15;
      break;
    case "bronze":
      discount = price * 0.05;
      break;
    default:
      discount = 0;
  }

  return discount;
}

function fetchData(url) {
  // WARNING 7: no-undef — 'fetch' may not be defined in older Node
  return fetch(url)
    .then((res) => res.json())
    .then((data) => {
      // WARNING 8: no-unused-vars — 'timestamp' assigned but never used
      const timestamp = Date.now();
      console.log("Fetched", data.length, "records");
      return data;
    });
}

function unreachableExample() {
  return 42;
  // WARNING 9: no-unreachable — code after return
  console.log("This line is never reached");
}

// WARNING 10: no-unused-vars — 'unusedHelper' is never used
function unusedHelper(a, b) {
  // WARNING 11: eqeqeq — using == instead of ===
  if (a == b) {
    return true;
  }
  return false;
}

module.exports = {
  processUserData,
  calculateDiscount,
  fetchData,
  unreachableExample,
};
