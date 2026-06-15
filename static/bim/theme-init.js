(function () {
    const storageKey = "bim-nexus-theme";
    const savedTheme = window.localStorage.getItem(storageKey);
    const theme = savedTheme === "light" ? "light" : "dark";
    document.documentElement.dataset.theme = theme;
})();
