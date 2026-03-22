import { NavLink, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import BookmarksPage from "./pages/BookmarksPage";
import LoginPage from "./pages/LoginPage";

const links = [
  { to: "/", label: "News" },
  { to: "/bookmarks", label: "Bookmarks" },
  { to: "/login", label: "Login" },
];

export default function App() {
  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#1c3d5a,_#09111a_45%,_#05070a)] text-slate-100">
      <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-4 py-6 sm:px-6">
        <header className="mb-8 flex flex-col gap-4 border-b border-white/10 pb-6 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-cyan-300/80">TrendByte</p>
            <h1 className="text-4xl font-semibold tracking-tight">Business and tech, without the noise.</h1>
          </div>
          <nav className="flex gap-2 rounded-full border border-white/10 bg-white/5 p-1">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  `rounded-full px-4 py-2 text-sm transition ${
                    isActive ? "bg-cyan-300 text-slate-950" : "text-slate-300 hover:bg-white/10"
                  }`
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
        </header>

        <main className="flex-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/bookmarks" element={<BookmarksPage />} />
            <Route path="/login" element={<LoginPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
