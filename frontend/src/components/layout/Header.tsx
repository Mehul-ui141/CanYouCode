import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

export default function Header() {
  const [isDark, setIsDark] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    const stored = localStorage.getItem("canyoucode_theme");
    if (stored === "light") {
      root.classList.remove("dark");
      root.classList.add("light");
      setIsDark(false);
    } else {
      root.classList.remove("light");
      root.classList.add("dark");
      setIsDark(true);
    }
  }, []);

  const toggleDarkMode = () => {
    const root = document.documentElement;
    if (isDark) {
      root.classList.remove("dark");
      root.classList.add("light");
      localStorage.setItem("canyoucode_theme", "light");
      setIsDark(false);
    } else {
      root.classList.remove("light");
      root.classList.add("dark");
      localStorage.setItem("canyoucode_theme", "dark");
      setIsDark(true);
    }
  };

  return (
    <>
      {/* Skip to content link */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:p-4 focus:bg-luxury-champagne focus:text-luxury-obsidian"
      >
        Skip to content
      </a>

      {/* Scroll progress bar */}
      <div className="fixed top-0 left-0 right-0 h-1 bg-luxury-champagne z-50 origin-left transition-all duration-150" id="scroll-progress" />

      {/* Fixed Header with solid background matching theme to prevent content bleed-through */}
      <header className="fixed top-0 left-0 right-0 z-40 bg-[var(--bg-header)] backdrop-blur-md border-b border-[var(--border-primary)] shadow-sm">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 group">
            <span className="text-2xl animate-pulse">🐍</span>
            <h1 className="text-xl font-bold tracking-tight">
              <span className="text-[var(--text-primary)] group-hover:opacity-80 transition-opacity">
                Can You
              </span>
              <span className="text-luxury-champagne group-hover:opacity-80 transition-opacity ml-1">
                Code
              </span>
            </h1>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link to="/" className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all hover:scale-105 transform">
              New Review
            </Link>
            <button
              onClick={toggleDarkMode}
              className="w-10 h-10 rounded-xl border border-[var(--border-primary)] bg-[var(--bg-card)] text-[var(--text-primary)] hover:border-luxury-champagne transition-all hover:scale-105 flex items-center justify-center cursor-pointer shadow-sm"
              title="Toggle Dark/Light Mode"
              aria-label="Toggle Dark/Light Mode"
            >
              {isDark ? (
                /* Perfectly centered symmetric Sun icon */
                <svg className="w-5 h-5 text-[var(--accent-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="5" />
                  <path strokeLinecap="round" d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42m12.72-12.72l1.42-1.42" />
                </svg>
              ) : (
                /* Perfectly centered classic Crescent Moon icon */
                <svg className="w-5 h-5 text-[var(--accent-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
                </svg>
              )}
            </button>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-all hover:scale-105 transform"
            >
              GitHub
            </a>
          </nav>

          {/* Mobile Menu Button */}
          <div className="flex items-center gap-3 md:hidden">
            <button
              onClick={toggleDarkMode}
              className="w-9 h-9 rounded-xl border border-[var(--border-primary)] bg-[var(--bg-card)] text-[var(--text-primary)] flex items-center justify-center cursor-pointer shadow-sm"
              aria-label="Toggle Dark/Light Mode"
            >
              {isDark ? (
                <svg className="w-4 h-4 text-luxury-champagne" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="5" />
                  <path strokeLinecap="round" d="M12 1v2m0 18v2M4.22 4.22l1.42 1.42m12.72 12.72l1.42 1.42M1 12h2m18 0h2M4.22 19.78l1.42-1.42m12.72-12.72l1.42-1.42" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-[var(--accent-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 12.79A9 9 0 1111.21 3 7 7 0 0021 12.79z" />
                </svg>
              )}
            </button>
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg border border-[var(--border-primary)] bg-[var(--bg-card)] text-[var(--text-primary)]"
              aria-label="Toggle mobile menu"
            >
              {mobileMenuOpen ? "✕" : "☰"}
            </button>
          </div>
        </div>

        {/* Mobile Dropdown Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-[var(--border-primary)] bg-[var(--bg-card)] px-4 py-4 space-y-3 shadow-lg">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="block text-[var(--text-secondary)] hover:text-[var(--text-primary)] py-2"
            >
              New Review
            </Link>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="block text-[var(--text-secondary)] hover:text-[var(--text-primary)] py-2"
            >
              GitHub
            </a>
          </div>
        )}
      </header>
    </>
  );
}
