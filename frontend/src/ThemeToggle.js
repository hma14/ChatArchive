export default function ThemeToggle({ dark, toggle }) {
  return (
    <button className="theme-btn" onClick={toggle}>
      {dark ? "☀ Light" : "🌙 Dark"}
    </button>
  );
}
