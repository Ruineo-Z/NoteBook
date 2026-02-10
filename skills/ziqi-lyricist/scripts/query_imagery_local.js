#!/usr/bin/env node

/**
 * 本地意象库查询脚本（Skill 版）
 *
 * 目标：在无 PromptX tool://imagery 运行时的情况下，
 * 直接从仓库 imagery_json 读取意象词，供 LLM 写词阶段使用。
 */

const fs = require('fs');
const path = require('path');

function printHelp(code = 0) {
  console.log(`
本地意象库查询

用法：
  node scripts/query_imagery_local.js --action list
  node scripts/query_imagery_local.js --action query --category 思念

参数：
  --action       list | query
  --category     类别名（query 时必填）
  --limit        返回数量，默认 120
  --imagery-dir  意象目录（可选）
  --with-count   query 时返回 count（默认 false，只返回 name）

说明：
  默认从仓库的 imagery_json 目录读取：../../../imagery_json
`);
  process.exit(code);
}

function parseArgs(argv) {
  const args = {
    action: null,
    category: null,
    limit: 120,
    imageryDir: null,
    withCount: false,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === '--action') {
      args.action = argv[++i];
    } else if (token === '--category') {
      args.category = argv[++i];
    } else if (token === '--limit') {
      args.limit = Number(argv[++i]);
    } else if (token === '--imagery-dir') {
      args.imageryDir = argv[++i];
    } else if (token === '--with-count') {
      args.withCount = true;
    } else if (token === '-h' || token === '--help') {
      printHelp(0);
    } else {
      console.error(`未知参数: ${token}`);
      printHelp(1);
    }
  }

  if (!args.action || !['list', 'query'].includes(args.action)) {
    console.error('参数错误: --action 必须是 list 或 query');
    printHelp(1);
  }

  if (args.action === 'query' && !args.category) {
    console.error('参数错误: query 模式必须提供 --category');
    printHelp(1);
  }

  if (!Number.isFinite(args.limit) || args.limit <= 0) {
    console.error('参数错误: --limit 必须为正数');
    process.exit(1);
  }

  return args;
}

function resolveImageryDir(inputDir) {
  if (inputDir) {
    return path.resolve(inputDir);
  }

  if (process.env.IMAGERY_DIR) {
    return path.resolve(process.env.IMAGERY_DIR);
  }

  return path.resolve(__dirname, '../../../imagery_json');
}

function listCategoryFiles(imageryDir) {
  if (!fs.existsSync(imageryDir)) {
    throw new Error(`意象目录不存在: ${imageryDir}`);
  }

  const files = fs
    .readdirSync(imageryDir)
    .filter((name) => name.endsWith('-imagery.json'))
    .sort((a, b) => a.localeCompare(b, 'zh-Hans-CN'));

  const categories = files.map((name) => name.replace(/-imagery\.json$/, ''));
  return { files, categories };
}

function readCategory(imageryDir, category) {
  const file = path.join(imageryDir, `${category}-imagery.json`);
  if (!fs.existsSync(file)) {
    throw new Error(`类别不存在: ${category}`);
  }

  const raw = fs.readFileSync(file, 'utf-8');
  const parsed = JSON.parse(raw);
  if (!Array.isArray(parsed)) {
    throw new Error(`数据格式错误: ${file}`);
  }

  return parsed;
}

function dedupeAndSort(items) {
  const map = new Map();

  for (const item of items) {
    if (!item || typeof item.name !== 'string') {
      continue;
    }

    const name = item.name.trim();
    if (!name) {
      continue;
    }

    const count = Number.isFinite(item.count) ? item.count : 0;
    const prev = map.get(name);
    if (!prev || count > prev.count) {
      map.set(name, { name, count });
    }
  }

  return [...map.values()].sort((a, b) => {
    if (b.count !== a.count) {
      return b.count - a.count;
    }
    return a.name.localeCompare(b.name, 'zh-Hans-CN');
  });
}

function main() {
  const args = parseArgs(process.argv);
  const imageryDir = resolveImageryDir(args.imageryDir);
  const { categories } = listCategoryFiles(imageryDir);

  if (args.action === 'list') {
    console.log(
      JSON.stringify(
        {
          success: true,
          imageryDir,
          categories,
          totalCategories: categories.length,
        },
        null,
        2,
      ),
    );
    return;
  }

  if (!categories.includes(args.category)) {
    console.log(
      JSON.stringify(
        {
          success: false,
          error: `不支持的类别: ${args.category}`,
          availableCategories: categories,
        },
        null,
        2,
      ),
    );
    process.exit(1);
  }

  const rows = readCategory(imageryDir, args.category);
  const cleaned = dedupeAndSort(rows);
  const selected = cleaned.slice(0, args.limit);

  const payload = {
    success: true,
    category: args.category,
    total: cleaned.length,
    returned: selected.length,
    imagery: args.withCount ? selected : selected.map((x) => x.name),
  };

  console.log(JSON.stringify(payload, null, 2));
}

try {
  main();
} catch (err) {
  console.error(`查询失败: ${err.message}`);
  process.exit(1);
}
