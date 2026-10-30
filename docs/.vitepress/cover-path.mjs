// VitePress does not automatically prefix URLs stored in frontmatter.
export function prefixCoverPath(image, base) {
  if (!image.startsWith('/') || image.startsWith('//') || base === '/' || image.startsWith(base)) return image
  return `${base}${image.slice(1)}`
}
