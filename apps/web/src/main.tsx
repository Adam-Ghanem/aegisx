import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { App } from "./App";
import "./styles.css";

const root = document.getElementById("root");
if (!root) throw new Error("Application root is missing");

ReactDOM.createRoot(root).render(
  <React.StrictMode><QueryClientProvider client={new QueryClient()}><App /></QueryClientProvider></React.StrictMode>,
);
