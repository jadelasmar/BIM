import { Search } from "../../constants/icons";

export default function SearchBar({
  value,
  onChange,
  placeholder,
  className = "",
  inputClassName = "",
  ...props
}) {
  return (
    <label className={`flex h-10 items-center gap-3 rounded-control border border-nexus-line bg-black px-3 text-zinc-500 transition-colors focus-within:border-[var(--bim-orange-focus)] focus-within:ring-2 focus-within:ring-[rgb(var(--bim-orange-focus-rgb)/20%)] ${className}`.trim()}>
      <Search className="h-4 w-4" aria-hidden="true" />
      <input
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={`w-full bg-transparent text-sm text-zinc-200 outline-none placeholder:text-zinc-600 ${inputClassName}`.trim()}
        {...props}
      />
    </label>
  );
}
