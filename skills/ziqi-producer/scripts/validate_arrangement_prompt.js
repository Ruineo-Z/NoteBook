#!/usr/bin/env node

/**
 * 编曲提示词格式校验（Skill 版）
 *
 * 校验目标：
 * 1) 五部分结构是否完整
 * 2) 是否出现禁止格式
 * 3) Suno 英文提示词字符数是否 <= 1000
 */

const fs = require('fs');
const path = require('path');

function help(code = 0) {
  console.log(`
编曲提示词校验

用法：
  node scripts/validate_arrangement_prompt.js --file /abs/path/song-arrangement.txt
`);
  process.exit(code);
}

function parseArgs(argv) {
  const args = { file: null };

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (token === '--file') {
      args.file = argv[++i];
    } else if (token === '-h' || token === '--help') {
      help(0);
    } else {
      console.error(`未知参数: ${token}`);
      help(1);
    }
  }

  if (!args.file) {
    console.error('缺少参数: --file');
    help(1);
  }

  return args;
}

function findLineNo(lines, pattern) {
  for (let i = 0; i < lines.length; i += 1) {
    if (pattern.test(lines[i])) {
      return i + 1;
    }
  }
  return 0;
}

function extractEnglishPromptBlock(text) {
  const lines = text.split(/\r?\n/);
  const startIdx = lines.findIndex((line) => line.trim() === '[Suno Prompt]');
  if (startIdx < 0) {
    return '';
  }

  let endIdx = lines.length;
  for (let i = startIdx + 1; i < lines.length; i += 1) {
    const s = lines[i].trim();
    if (
      s.startsWith('【编曲提示词 - 中文版】') ||
      s.startsWith('【中文版') ||
      s.startsWith('---') ||
      s.startsWith('=====')
    ) {
      endIdx = i;
      break;
    }
  }

  return lines.slice(startIdx, endIdx).join('\n').trim();
}

function main() {
  const { file } = parseArgs(process.argv);
  const abs = path.resolve(file);

  if (!fs.existsSync(abs)) {
    throw new Error(`文件不存在: ${abs}`);
  }

  const text = fs.readFileSync(abs, 'utf-8');
  const lines = text.split(/\r?\n/);
  const issues = [];

  const requiredTags = ['[Suno Prompt]', '[Style]', '[Lead]', '[Backing]', '[Vocals]', '[Structure]'];
  for (const tag of requiredTags) {
    if (!text.includes(tag)) {
      issues.push({
        line: 0,
        code: 'MISSING_TAG',
        message: `缺少必需标签: ${tag}`,
      });
    }
  }

  // 禁止格式
  const forbiddenPatterns = [
    { regex: /^\s*Title\s*:/i, code: 'FORBIDDEN_TITLE_COLON', message: '禁止使用 `Title:` 格式。' },
    { regex: /^\s*Style\s*Tags\s*:/i, code: 'FORBIDDEN_STYLE_TAGS_COLON', message: '禁止使用 `Style Tags:` 格式。' },
    { regex: /^\s*Prompt\s*:/i, code: 'FORBIDDEN_PROMPT_COLON', message: '禁止使用 `Prompt:` 格式。' },
    { regex: /^\s*\[\s*Genre\s*:\s*.*\]\s*$/i, code: 'FORBIDDEN_GENRE_TAG', message: '禁止使用 `[Genre:]` 标签。' },
    { regex: /^\s*\[\s*Instruments\s*:\s*.*\]\s*$/i, code: 'FORBIDDEN_INSTRUMENTS_TAG', message: '禁止使用 `[Instruments:]` 标签。' },
    { regex: /^\s*#{1,6}\s+/, code: 'FORBIDDEN_MARKDOWN_HEADING', message: '禁止使用 Markdown 标题格式。' },
    { regex: /^\s*\*\*[^*]+:\*\*\s*$/, code: 'FORBIDDEN_MARKDOWN_BOLD_LABEL', message: '禁止使用 Markdown 粗体标签格式。' },
  ];

  for (const rule of forbiddenPatterns) {
    const n = findLineNo(lines, rule.regex);
    if (n > 0) {
      issues.push({ line: n, code: rule.code, message: rule.message });
    }
  }

  const promptBlock = extractEnglishPromptBlock(text);
  const promptLength = promptBlock.length;

  if (!promptBlock) {
    issues.push({
      line: 0,
      code: 'MISSING_PROMPT_BLOCK',
      message: '未找到 `[Suno Prompt]` 英文提示词区块。',
    });
  } else if (promptLength > 1000) {
    issues.push({
      line: 0,
      code: 'PROMPT_TOO_LONG',
      message: `英文提示词区块字符数为 ${promptLength}，超过 1000。`,
    });
  }

  const result = {
    success: issues.length === 0,
    file: abs,
    promptLength,
    issueCount: issues.length,
    issues,
  };

  console.log(JSON.stringify(result, null, 2));
  process.exit(result.success ? 0 : 2);
}

try {
  main();
} catch (err) {
  console.error(`校验失败: ${err.message}`);
  process.exit(1);
}
