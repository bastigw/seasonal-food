// Builds a 12-month CO2e series for a single food item, by scanning every
// month's vegetable/fruit groups for a matching item id. Items are absent
// from months where they're out of season, which shows up as `present:
// false` entries so the chart can render a gap instead of a false zero.
export function buildItemSeries(data, country, itemId) {
  const months = data[country]
  const series = []
  let latestItem = null

  for (let month = 1; month <= 12; month++) {
    const groups = [...months[String(month)].vegetable, ...months[String(month)].fruit]
    let found = null
    for (const group of groups) {
      const match = group.items.find((item) => item.id === itemId)
      if (match) {
        found = match
        break
      }
    }
    if (found) latestItem = found
    series.push(
      found
        ? { month, present: true, value: found.kgCo2ePerKg, tier: found.tier, item: found }
        : { month, present: false, value: null, tier: null, item: null }
    )
  }

  return { series, item: latestItem }
}
