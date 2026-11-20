'use client';

import React, { useState } from 'react';

interface MarkdownRendererProps {
  content: string;
}

interface CodeBlockProps {
  language: string;
  code: string;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      if (typeof navigator !== 'undefined' && navigator.clipboard) {
        await navigator.clipboard.writeText(code);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      }
    } catch {
      // Fallback
    }
  };

  return (
    <div className="my-3 rounded-xl overflow-hidden border border-slate-700/60 bg-slate-950 shadow-sm text-xs">
      <div className="flex items-center justify-between px-3.5 py-1.5 bg-slate-900 border-b border-slate-800 text-[11px] text-slate-400 font-mono">
        <span className="uppercase font-semibold tracking-wider text-emerald-400">
          {language || 'code'}
        </span>
        <button
          type="button"
          onClick={handleCopy}
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded hover:bg-slate-800 text-slate-300 hover:text-white transition-colors"
          title="Copy to clipboard"
        >
          {copied ? (
            <span className="text-emerald-400 font-semibold">✓ Copied</span>
          ) : (
            <span>📋 Copy</span>
          )}
        </button>
      </div>
      <pre className="p-3.5 overflow-x-auto font-mono text-slate-200 leading-relaxed text-[11.5px]">
        <code>{code}</code>
      </pre>
    </div>
  );
};

function renderInlineText(text: string): React.ReactNode[] {
  // Regex parsing for inline elements: `code`, **bold**, *italic*, [link](url)
  const tokens: React.ReactNode[] = [];
  const inlineRegex = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]+\]\([^)]+\))/g;

  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = inlineRegex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      tokens.push(text.slice(lastIndex, match.index));
    }
    const token = match[0];
    if (token.startsWith('`') && token.endsWith('`')) {
      tokens.push(
        <code
          key={match.index}
          className="px-1.5 py-0.5 rounded-md bg-slate-100 dark:bg-slate-800 text-emerald-700 dark:text-emerald-300 font-mono text-[11px] border border-slate-200 dark:border-slate-700"
        >
          {token.slice(1, -1)}
        </code>
      );
    } else if (token.startsWith('**') && token.endsWith('**')) {
      tokens.push(
        <strong key={match.index} className="font-bold text-slate-900 dark:text-white">
          {token.slice(2, -2)}
        </strong>
      );
    } else if (token.startsWith('*') && token.endsWith('*')) {
      tokens.push(
        <em key={match.index} className="italic text-slate-800 dark:text-slate-200">
          {token.slice(1, -1)}
        </em>
      );
    } else if (token.startsWith('[') && token.includes('](')) {
      const closingBracket = token.indexOf('](');
      const linkText = token.slice(1, closingBracket);
      const linkUrl = token.slice(closingBracket + 2, -1);
      tokens.push(
        <a
          key={match.index}
          href={linkUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-emerald-600 dark:text-emerald-400 underline hover:text-emerald-500 font-medium"
        >
          {linkText}
        </a>
      );
    }
    lastIndex = match.index + token.length;
  }

  if (lastIndex < text.length) {
    tokens.push(text.slice(lastIndex));
  }

  return tokens.length > 0 ? tokens : [text];
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  // Parse content into blocks (code blocks, headings, lists, tables, paragraphs)
  const blocks: React.ReactNode[] = [];
  const lines = content.split('\n');
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // 1. Code Block detection
    if (line.trim().startsWith('```')) {
      const language = line.trim().slice(3).trim();
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // Skip closing ```
      blocks.push(
        <CodeBlock
          key={`code-${i}`}
          language={language}
          code={codeLines.join('\n')}
        />
      );
      continue;
    }

    // 2. Headings
    if (line.startsWith('### ')) {
      blocks.push(
        <h3
          key={`h3-${i}`}
          className="text-sm font-bold text-slate-900 dark:text-white mt-4 mb-2 flex items-center gap-1.5"
        >
          <span className="text-emerald-500">#</span>
          {renderInlineText(line.slice(4))}
        </h3>
      );
      i++;
      continue;
    }
    if (line.startsWith('## ')) {
      blocks.push(
        <h2
          key={`h2-${i}`}
          className="text-base font-extrabold text-slate-900 dark:text-white mt-5 mb-2.5 pb-1 border-b border-slate-200 dark:border-slate-800"
        >
          {renderInlineText(line.slice(3))}
        </h2>
      );
      i++;
      continue;
    }
    if (line.startsWith('# ')) {
      blocks.push(
        <h1
          key={`h1-${i}`}
          className="text-lg font-black text-slate-900 dark:text-white mt-6 mb-3"
        >
          {renderInlineText(line.slice(2))}
        </h1>
      );
      i++;
      continue;
    }

    // 3. Blockquotes
    if (line.startsWith('> ')) {
      const quoteLines: string[] = [line.slice(2)];
      i++;
      while (i < lines.length && lines[i].startsWith('> ')) {
        quoteLines.push(lines[i].slice(2));
        i++;
      }
      blocks.push(
        <blockquote
          key={`quote-${i}`}
          className="my-3 pl-3.5 border-l-2 border-emerald-500 bg-emerald-500/5 py-1.5 rounded-r-lg text-slate-700 dark:text-slate-300 italic text-xs"
        >
          {quoteLines.map((q, idx) => (
            <p key={idx}>{renderInlineText(q)}</p>
          ))}
        </blockquote>
      );
      continue;
    }

    // 4. Bullet lists
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      const listItems: { text: string; indent: number }[] = [];
      while (
        i < lines.length &&
        (lines[i].trim().startsWith('- ') || lines[i].trim().startsWith('* '))
      ) {
        const itemLine = lines[i];
        const indent = itemLine.search(/\S/);
        listItems.push({
          text: itemLine.trim().slice(2),
          indent,
        });
        i++;
      }
      blocks.push(
        <ul key={`ul-${i}`} className="my-2.5 space-y-1.5 pl-4 text-xs">
          {listItems.map((item, idx) => (
            <li
              key={idx}
              style={{ marginLeft: `${item.indent * 0.5}rem` }}
              className="list-disc text-slate-700 dark:text-slate-300 leading-relaxed"
            >
              {renderInlineText(item.text)}
            </li>
          ))}
        </ul>
      );
      continue;
    }

    // 5. Numbered lists
    if (/^\s*\d+\.\s+/.test(line)) {
      const listItems: string[] = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        const itemText = lines[i].replace(/^\s*\d+\.\s+/, '');
        listItems.push(itemText);
        i++;
      }
      blocks.push(
        <ol key={`ol-${i}`} className="my-2.5 space-y-1.5 pl-4 list-decimal text-xs text-slate-700 dark:text-slate-300">
          {listItems.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              {renderInlineText(item)}
            </li>
          ))}
        </ol>
      );
      continue;
    }

    // 6. Tables
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      const tableLines: string[] = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        tableLines.push(lines[i]);
        i++;
      }
      if (tableLines.length >= 2) {
        const headers = tableLines[0]
          .split('|')
          .slice(1, -1)
          .map((c) => c.trim());
        const rowLines = tableLines.slice(2);
        blocks.push(
          <div key={`table-${i}`} className="my-3 overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800 text-xs">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 dark:bg-slate-900/80">
                <tr>
                  {headers.map((h, hIdx) => (
                    <th
                      key={hIdx}
                      className="px-3 py-2 text-left text-[11px] font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider"
                    >
                      {renderInlineText(h)}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/60 bg-white dark:bg-slate-950/40">
                {rowLines.map((row, rIdx) => {
                  const cells = row
                    .split('|')
                    .slice(1, -1)
                    .map((c) => c.trim());
                  return (
                    <tr key={rIdx} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/50">
                      {cells.map((cell, cIdx) => (
                        <td key={cIdx} className="px-3 py-2 text-slate-700 dark:text-slate-300">
                          {renderInlineText(cell)}
                        </td>
                      ))}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        );
        continue;
      }
    }

    // 7. Regular paragraph / empty line
    if (line.trim().length === 0) {
      i++;
      continue;
    }

    blocks.push(
      <p key={`p-${i}`} className="my-1.5 leading-relaxed text-slate-700 dark:text-slate-200 text-xs">
        {renderInlineText(line)}
      </p>
    );
    i++;
  }

  return <div className="space-y-1">{blocks}</div>;
};
