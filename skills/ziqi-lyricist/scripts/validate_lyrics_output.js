#!/usr/bin/env node

/**
 * 歌词输出格式校验（Skill 版）
 *
 * 仅做格式层面的硬约束检查，不做语义质量判断。
 */

const fs = require('fs');
const path = require('path');

function printHelp(code = 0) {
  console.log(`
歌词输出格式校验

用法：
  node scripts/validate_lyrics_output.js --file /abs/path/song-lyrics.txt

参数：
  --file      待校验歌词文件
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
      printHelp(0);
    } else {
      console.error(`未知参数: ${token}`);
      printHelp(1);
    }
  }

  if (!args.file) {
    console.error('缺少参数: --file');
    printHelp(1);
  }

  return args;
}

function main() {
  const args = parseArgs(process.argv);
  const file = path.resolve(args.file);

  if (!fs.existsSync(file)) {
    throw new Error(`文件不存在: ${file}`);
  }

  const lines = fs.readFileSync(file, 'utf-8').split(/\r?\n/);

  const issues = [];
  let hasTag = false;

  lines.forEach((line, idx) => {
    const n = idx + 1;
    const s = line.trim();
    if (!s) return;

    if (/^\[\d{2}:\d{2}\.\d{2,3}\]/.test(s)) {
      issues.push({ line: n, code: 'TIMESTAMP_FOUND', message: '检测到时间戳格式，输出歌词禁止使用LRC时间戳。' });
    }

    if (/^#{1,6}\s+/.test(s)) {
      issues.push({ line: n, code: 'MARKDOWN_HEADING_FOUND', message: '检测到Markdown标题格式，输出歌词需使用Suno标签。' });
    }

    if (/^\([^)]+\)$/.test(s)) {
      issues.push({ line: n, code: 'PAREN_TAG_FOUND', message: '检测到圆括号段落标签，需改为方括号标签。' });
    }

    if (/^\[[^\]]+\]$/.test(s)) {
      hasTag = true;
    }
  });

  if (!hasTag) {
    issues.push({ line: 0, code: 'NO_SUNO_TAG', message: '未检测到Suno段落标签（如 [Verse 1] / [Chorus - Powerful & Emotional]）。' });
  }

  const result = {
    success: issues.length === 0,
    file,
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
