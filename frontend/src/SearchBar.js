export default function SearchBar({ search, setSearch }) {
  return (
    <input
      className="search-bar"
      placeholder="Search conversations..."
      value={search}
      onChange={(e) => setSearch(e.target.value)}
    />
  );
}
