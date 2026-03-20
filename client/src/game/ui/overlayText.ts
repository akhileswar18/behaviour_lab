const MAX_OVERLAY_CHARS = 60;

function truncateWithEllipsis(content: string, maxChars = MAX_OVERLAY_CHARS): string {
  if (content.length <= maxChars) {
    return content;
  }
  return `${content.slice(0, Math.max(0, maxChars - 1)).trimEnd()}...`;
}

function cleanupDebugSuffix(content: string): string {
  return content
    .replace(/\swith\s+risk=.*?(?=[.!?](?:\s|$)|$)/gi, "")
    .replace(/\s{2,}/g, " ")
    .trim();
}

function firstSentence(content: string): string {
  const sentenceWithPunctuation = content.match(/^.+?[.!?](?=\s+|$)/)?.[0]?.trim();
  if (sentenceWithPunctuation) {
    return sentenceWithPunctuation;
  }
  return content.trim();
}

export function formatSpeechBubbleText(content: string): string {
  if (!content.trim()) {
    return "";
  }
  const cleanedSource = cleanupDebugSuffix(content);
  const sentence = firstSentence(cleanedSource);
  const cleaned = sentence.replace(/\s{2,}/g, " ").trim();
  const clipped = truncateWithEllipsis(cleaned);
  const debugStripped = cleanedSource !== content.trim();
  if (debugStripped && !clipped.endsWith("...")) {
    return `${clipped.replace(/[.!?]+$/, "")}...`;
  }
  return clipped;
}

export function formatThoughtBubbleText(content: string): string {
  if (!content.trim()) {
    return "";
  }
  return truncateWithEllipsis(firstSentence(content).replace(/\s{2,}/g, " ").trim());
}
