export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        nexus: {
          page: "#070707",
          panel: "#161616",
          panel2: "#1f1f1f",
          line: "#2a2a2a",
          muted: "#a1a1aa",
          orange: "#f59e0b",
          green: "#00c896",
          red: "#ff3b4f",
          blue: "#38a3ff",
          purple: "#8b5cf6"
        }
      },
      boxShadow: {
        panel: "0 1px 0 rgba(255,255,255,0.04) inset"
      }
    }
  },
  plugins: []
};
