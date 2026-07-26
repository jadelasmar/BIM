// Fixed categorical palette for the Command Center stock status chart's
// three bars (Reserved/Issued/Repair -- Available is shown as a context
// stat, not a bar, and Removed doesn't belong alongside these active
// statuses at all). These hexes (and their order) are an internal slice of
// the dataviz skill's validated 8-slot sequence -- validated as a set with
// `validate_palette.js` for both CVD adjacency and light/dark contrast
// (dropping slots from either end of an already-validated adjacent
// sequence can't introduce a new adjacency between the ones that remain,
// so this 3-slot slice stays valid without re-running it). Do not reorder
// or reassign a slot to a different status without re-validating: the
// sequence itself is the colorblind-safety mechanism, not a cosmetic
// choice. Intentionally its own palette rather than the shared status-badge
// colors in statusStyles.js -- those reuse the same hue (red) for both
// "repair" and "removed", which would be ambiguous as adjacent chart bars.
export const STOCK_STATUS_COLORS = {
  reserved: { light: "#eb6834", dark: "#d95926" },
  issued: { light: "#1baf7a", dark: "#199e70" },
  repair: { light: "#eda100", dark: "#c98500" }
};
