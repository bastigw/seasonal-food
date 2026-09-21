// Static UI copy, keyed semantically. Every hardcoded string in the Vue
// components lives here so components can render `strings[lang].key`.
export const strings = {
  en: {
    pageTitle: 'Climate Impact of Produce',
    countryNav: 'Country',
    languageSelect: 'Language',
    emptyState: 'Nothing tracked for this month yet.',
    vegetables: 'Vegetables',
    fruit: 'Fruit',
    prevMonth: 'Previous month',
    nextMonth: 'Next month',
    selectMonth: 'Select month',
    legend: 'kg CO₂e per 500 g, most likely supply route. Lower is better.',
    short: '{n}% short trip',
    far: '{n}% far away',
    tierLow: 'low impact',
    tierMedium: 'medium impact',
    tierHigh: 'high impact',
    roughEstimate: 'Rough estimate: thin or mixed data',
    disclaimer:
      'Estimates modelled from trade and production statistics (Eurostat, HMRC, EUFIC), not measurements. Footprints are approximate.',
  },
  de: {
    pageTitle: 'Klimawirkung von Obst & Gemüse',
    countryNav: 'Land',
    languageSelect: 'Sprache',
    emptyState: 'Für diesen Monat sind noch keine Daten erfasst.',
    vegetables: 'Gemüse',
    fruit: 'Obst',
    prevMonth: 'Vorheriger Monat',
    nextMonth: 'Nächster Monat',
    selectMonth: 'Monat auswählen',
    legend: 'kg CO₂e pro 500 g, wahrscheinlichster Lieferweg. Weniger ist besser.',
    short: '{n}% kurzer Weg',
    far: '{n}% weiter Weg',
    tierLow: 'geringe Wirkung',
    tierMedium: 'mittlere Wirkung',
    tierHigh: 'hohe Wirkung',
    roughEstimate: 'Grobe Schätzung: dünne oder gemischte Datenlage',
    disclaimer:
      'Schätzungen auf Basis von Handels- und Erzeugungsstatistiken (Eurostat, HMRC, EUFIC), keine Messwerte. Die Werte sind Näherungen.',
  },
}
