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
    <label className={`flex h-10 items-center gap-3 rounded-md border border-nexus-line bg-black px-3 text-zinc-500 ${className}`.trim()}>
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
