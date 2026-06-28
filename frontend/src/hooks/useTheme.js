export const DEFAULT_THEME_STORAGE_KEY = "bim-nexus-theme";

export function currentTheme() {
  return document.documentElement.dataset.theme === "light" ? "light" : "dark";
}

export function applyTheme(nextTheme, storageKey = DEFAULT_THEME_STORAGE_KEY) {
  const normalizedTheme = nextTheme === "light" ? "light" : "dark";
  document.documentElement.dataset.theme = normalizedTheme;
  window.localStorage.setItem(storageKey, normalizedTheme);
  document.dispatchEvent(new CustomEvent("bim-nexus-theme-change", { detail: normalizedTheme }));
  return normalizedTheme;
}
