export function formatMarkdown(text: string): string {
  if (!text) return '';
  
  const lines = text.split('\n');
  let html = '';
  let inList = false;
  let inParagraph = false;
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    
    if (!line) {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (inParagraph) {
        html += '</p>';
        inParagraph = false;
      }
      continue;
    }
    
    if (line.startsWith('#### ')) {
      if (inList) { html += '</ul>'; inList = false; }
      if (inParagraph) { html += '</p>'; inParagraph = false; }
      html += `<h4>${escapeHtml(line.substring(5))}</h4>`;
    } else if (line.startsWith('### ')) {
      if (inList) { html += '</ul>'; inList = false; }
      if (inParagraph) { html += '</p>'; inParagraph = false; }
      html += `<h3>${escapeHtml(line.substring(4))}</h3>`;
    } else if (line.startsWith('## ')) {
      if (inList) { html += '</ul>'; inList = false; }
      if (inParagraph) { html += '</p>'; inParagraph = false; }
      html += `<h2>${escapeHtml(line.substring(3))}</h2>`;
    } else if (line.startsWith('# ')) {
      if (inList) { html += '</ul>'; inList = false; }
      if (inParagraph) { html += '</p>'; inParagraph = false; }
      html += `<h1>${escapeHtml(line.substring(2))}</h1>`;
    } else if (line.startsWith('---')) {
      if (inList) { html += '</ul>'; inList = false; }
      if (inParagraph) { html += '</p>'; inParagraph = false; }
      html += '<hr>';
    } else if (line.match(/^[\-\*] /) || line.match(/^\d+\. /)) {
      if (!inList) {
        if (inParagraph) { html += '</p>'; inParagraph = false; }
        html += '<ul>';
        inList = true;
      }
      const listContent = line.replace(/^[\-\*] /, '').replace(/^\d+\. /, '');
      html += `<li>${processInlineMarkdown(listContent)}</li>`;
    } else {
      if (inList) {
        html += '</ul>';
        inList = false;
      }
      if (!inParagraph) {
        html += '<p>';
        inParagraph = true;
      } else {
        html += '<br>';
      }
      html += processInlineMarkdown(line);
    }
  }
  
  if (inList) html += '</ul>';
  if (inParagraph) html += '</p>';
  
  return html;
}

function processInlineMarkdown(text: string): string {
  return escapeHtml(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/__(.*?)__/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/_(.*?)_/g, '<em>$1</em>')
    .replace(/`(.*?)`/g, '<code>$1</code>');
}

function escapeHtml(text: string): string {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

