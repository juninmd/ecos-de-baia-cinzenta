// Escolha de voz da narração: vozes pt-BR primeiro; mantém a escolhida se ainda existir;
// senão segue a preferência histórica (Daniel/Microsoft, depois qualquer não-Google).
export function pickVoices(all, current) {
  const pt = all.filter((v) => /^pt[-_]BR$/i.test(v.lang))
  const list = pt.length ? pt : all
  if (list.some((v) => v.name === current)) return { list, name: current }
  const preferred = list.find((v) => /Daniel|Microsoft|Felipe|Ricardo/.test(v.name)) ?? list.find((v) => !/Google/.test(v.name))
  return { list, name: (preferred ?? list[0])?.name ?? '' }
}
