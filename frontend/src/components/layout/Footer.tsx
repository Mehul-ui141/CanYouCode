import { useState } from "react";

export default function Footer() {
  const [cookieAccepted, setCookieAccepted] = useState(
    () => localStorage.getItem("canyoucode_cookie_accepted") === "true"
  );
  const [contactOpen, setContactOpen] = useState(false);
  const [contactSent, setContactSent] = useState(false);

  const acceptCookies = () => {
    localStorage.setItem("canyoucode_cookie_accepted", "true");
    setCookieAccepted(true);
  };

  return (
    <footer className="border-t border-zinc-800 py-6 mt-auto bg-zinc-950 text-zinc-400 relative">
      <div className="max-w-6xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between text-xs text-zinc-500 gap-4">
        <div className="space-y-1 text-center sm:text-left">
          {/* Removed unwanted text */}
        </div>

        <div className="flex items-center gap-4">
          <button
            onClick={() => setContactOpen(true)}
            className="px-3 py-1.5 rounded-lg border transition-colors luxury-button cursor-pointer"
          >
            💬 Feedback / Contact
          </button>
        </div>
      </div>

      {/* Floating Cookie Banner */}
      {!cookieAccepted && (
        <div className="fixed bottom-4 left-4 right-4 sm:left-auto sm:right-4 sm:max-w-md bg-zinc-900 border border-zinc-700 p-4 rounded-2xl shadow-2xl z-50 flex items-center justify-between gap-4 animate-bounce-short">
          <p className="text-xs text-zinc-300">
            🍪 We use cookies and local storage to save your review history and preferences.
          </p>
          <button
            onClick={acceptCookies}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-xl text-xs font-bold whitespace-nowrap transition-transform hover:scale-105 cursor-pointer"
          >
            Accept
          </button>
        </div>
      )}

      {/* Floating Contact Modal */}
      {contactOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="border rounded-2xl max-w-md w-full p-6 space-y-4 modal-backdrop">
            <h3 className="text-lg font-bold">Send Feedback</h3>
            {contactSent ? (
              <div className="p-4 rounded-xl text-sm border">
                Thank you! Your feedback has been received.
              </div>
            ) : (
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  setContactSent(true);
                  setTimeout(() => {
                    setContactSent(false);
                    setContactOpen(false);
                  }, 2000);
                }}
                className="space-y-3"
              >
                <textarea
                  required
                  rows={4}
                  placeholder="Tell us what you think or report a bug..."
                  className="w-full rounded-xl p-3 text-sm focus:outline-none focus:border luxury-accent-button"
                />
                <div className="flex justify-end gap-2">
                  <button
                    type="button"
                    onClick={() => setContactOpen(false)}
                    className="px-4 py-2 text-xs font-medium cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 rounded-xl text-xs font-bold cursor-pointer luxury-accent-button"
                  >
                    Send Feedback
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </footer>
  );
}
