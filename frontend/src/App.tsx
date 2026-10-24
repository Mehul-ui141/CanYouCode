import { BrowserRouter, Route, Routes } from "react-router-dom";
import Header from "./components/layout/Header";
import Footer from "./components/layout/Footer";
import HomePage from "./pages/HomePage";
import ReviewPage from "./pages/ReviewPage";
import NotFoundPage from "./pages/NotFoundPage";
import ScrollToTop from "./components/ui/ScrollToTop";

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen bg-zinc-950 text-zinc-100 antialiased selection:bg-red-500 selection:text-white">
        <Header />
        <main id="main-content" className="flex-1 w-full px-4">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/review/:reviewId" element={<ReviewPage />} />
            <Route path="/review/share/:shareToken" element={<ReviewPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <Footer />
        <ScrollToTop />
      </div>
    </BrowserRouter>
  );
}
