import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App.jsx";
import "./styles.css";

function readInitialData() {
  const node = document.getElementById("bim-nexus-initial-data");
  if (!node) {
    return null;
  }

  try {
    return JSON.parse(node.textContent);
  } catch (error) {
    console.error("Could not parse BIM Nexus initial data", error);
    return null;
  }
}

createRoot(document.getElementById("bim-nexus-root")).render(
  <React.StrictMode>
    <App initialData={readInitialData()} />
  </React.StrictMode>
);
