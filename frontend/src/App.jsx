// src/App.jsx

import { BrowserRouter, Routes, Route } from "react-router-dom";

import Navbar from "./components/Navbar";

import UploadPage from "./pages/UploadPage";
import AskPage from "./pages/AskPage";
import AnalyzePage from "./pages/AnalyzePage";
import PapersPage from "./pages/PapersPage";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-100">

        <Navbar />

        <main className="container mx-auto px-6 py-8">

          <Routes>

            <Route
              path="/"
              element={<UploadPage />}
            />

            <Route
              path="/ask"
              element={<AskPage />}
            />

            <Route
              path="/analyze"
              element={<AnalyzePage />}
            />

            <Route
              path="/papers"
              element={<PapersPage />}
            />

          </Routes>

        </main>

      </div>
    </BrowserRouter>
  );
}