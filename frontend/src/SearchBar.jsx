import { useState } from "react"

const SearchBar = () => {
  const [query, setQuery] = useState("")

  return (
    <div className="flex gap-2">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Effectuez une recherche"
        className="flex-1 border border-slate-300 rounded-lg px-4 py-2 text-sm text-slate-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
      <button className="px-4 py-2 bg-gray-500 text-white text-sm rounded-lg">
        Rechercher
      </button>
    </div>
  )
}

export default SearchBar