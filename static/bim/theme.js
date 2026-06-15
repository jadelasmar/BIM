(function () {
    const storageKey = "bim-nexus-theme";

    function getTheme() {
        return document.documentElement.dataset.theme === "light" ? "light" : "dark";
    }

    function setTheme(theme) {
        const nextTheme = theme === "light" ? "light" : "dark";
        document.documentElement.dataset.theme = nextTheme;
        window.localStorage.setItem(storageKey, nextTheme);
        document.dispatchEvent(new CustomEvent("bim-nexus-theme-change", { detail: nextTheme }));
    }

    function toggleTheme() {
        setTheme(getTheme() === "light" ? "dark" : "light");
    }

    window.BimNexusTheme = {
        storageKey,
        getTheme,
        setTheme,
        toggleTheme,
    };

    document.addEventListener("DOMContentLoaded", function () {
        document.querySelectorAll("[data-theme-toggle]").forEach(function (toggle) {
            toggle.addEventListener("click", toggleTheme);
        });
    });
})();
