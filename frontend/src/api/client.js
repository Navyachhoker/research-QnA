// src/api/client.js

import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  headers: {
    "Content-Type": "application/json",
  },
});

// ---------------- Papers ----------------

export const uploadPaper = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  return api.post("/papers/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
};

export const listPapers = async () => {
  return api.get("/papers/list");
};

// ---------------- Q&A ----------------

export const askQuestion = async (
  question,
  paper = null,
  top_k = 5
) => {
  return api.post("/qa/ask", {
    question,
    paper,
    top_k,
  });
};

// ---------------- Analysis ----------------

export const summarizePaper = async (paper_name) => {
  return api.post("/analysis/summarize", {
    paper_name,
  });
};

export const comparePapers = async (
  paper_a,
  paper_b
) => {
  return api.post("/analysis/compare", {
    paper_a,
    paper_b,
  });
};

export const generateRelatedWork = async (topic) => {
  return api.post("/analysis/related-work", {
    topic,
  });
};

export default api;