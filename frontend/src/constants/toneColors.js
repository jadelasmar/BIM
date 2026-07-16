// Single source of truth for every "soft chip" background+text class pair used by
// the app's three tone-mapping systems: statusStyles.js, uiRegistry.js, and
// components/ui/Badge.jsx's own local tone map. Those three previously hardcoded
// these strings independently, in three different naming conventions, with no
// shared vocabulary — see the design-system audit for the full picture.
//
// Color fix (this pass): the 19 entries that failed light-mode contrast now use a
// theme-aware text color instead of a flat Tailwind -400 class. Entries whose text
// was already a --bim-*/nexus-* token (redSoft10Nexus, emeraldSoft10Nexus,
// blueSoft10Nexus, violetSoft10Nexus) needed no edit here at all -- they inherited
// the fix automatically once the base token got a light-mode value in styles.css.
// amberSoft15Nexus/amberSoft10Nexus were repointed at the existing --bim-orange-text
// token (added in the auth-page pass) rather than duplicating a new orange value.
// The other 13 get their own --tone-*-text custom property (see styles.css) since
// there was no existing token for those hues. Backgrounds are untouched throughout --
// only text color changed, and only where light mode required it.
export const TONE_COLORS = {
  redSoft15: "bg-red-500/15 text-[var(--tone-red-text)]",
  redSoft10Nexus: "bg-red-500/10 text-nexus-red",

  greenSoft15: "bg-green-500/15 text-[var(--tone-green-text)]",

  emeraldSoft15: "bg-emerald-500/15 text-[var(--tone-emerald-text)]",
  emeraldSoft10Nexus: "bg-emerald-500/10 text-nexus-green",

  blueSoft15: "bg-blue-500/15 text-[var(--tone-blue-text)]",
  blueSoft10Nexus: "bg-blue-500/10 text-nexus-blue",

  amberSoft15Amber: "bg-amber-500/15 text-[var(--tone-amber-text)]",
  amberSoft15Nexus: "bg-amber-500/15 text-[var(--bim-orange-text)]",
  amberSoft10Nexus: "bg-amber-500/10 text-[var(--bim-orange-text)]",

  zincSoft15: "bg-zinc-500/15 text-zinc-400",
  zincSoft10: "bg-zinc-500/10 text-zinc-400",
  zinc70060: "bg-zinc-700/60 text-zinc-300",

  indigoSoft15: "bg-indigo-500/15 text-[var(--tone-indigo-text)]",
  indigoSoft10: "bg-indigo-500/10 text-[var(--tone-indigo-text)]",

  cyanSoft15: "bg-cyan-500/15 text-[var(--tone-cyan-text)]",
  cyanSoft10: "bg-cyan-500/10 text-[var(--tone-cyan-text)]",

  purpleSoft15: "bg-purple-500/15 text-[var(--tone-purple-text)]",
  violetSoft10Nexus: "bg-violet-500/10 text-nexus-purple",

  skySoft15: "bg-sky-500/15 text-[var(--tone-sky-text)]",
  skySoft10: "bg-sky-500/10 text-[var(--tone-sky-text)]",

  yellowSoft10: "bg-yellow-500/10 text-[var(--tone-yellow-text)]"
};
