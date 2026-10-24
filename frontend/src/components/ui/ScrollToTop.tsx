import { useEffect, useState } from "react";

export default function ScrollToTop() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      // Update scroll progress bar
      const winScroll = document.documentElement.scrollTop;
      const height =
        document.documentElement.scrollHeight -
        document.documentElement.clientHeight;
      const scrolled = winScroll / height;
      const progressBar = document.getElementById("scroll-progress");
      if (progressBar) {
        progressBar.style.transform = `scaleX(${scrolled})`;
      }

      if (window.scrollY > 300) {
        setVisible(true);
      } else {
        setVisible(false);
      }
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  if (!visible) return null;

  return (
    <button
      onClick={scrollToTop}
      className="fixed bottom-6 right-6 z-40 p-3 rounded-full transition-all duration-300 luxury-button scroll-to-top"
      aria-label="Scroll back to top"
      title="Scroll back to top"
    >
      ↑
    </button>
  );
}
