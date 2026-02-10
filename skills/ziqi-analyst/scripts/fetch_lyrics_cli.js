#!/usr/bin/env node

/**
 * 歌词抓取（Codex/CLI 版）
 *
 * 目标：替代 PromptX 的 lyrics-fetcher 运行时依赖。
 * 输出：带时间戳的歌词 txt，格式兼容 ziqi-analyst。
 */

const fs = require("fs");
const path = require("path");
const https = require("https");
const http = require("http");

const SHORT_LINK_DOMAINS = ["c6.y.qq.com", "c.y.qq.com", "i.y.qq.com"];

const PLATFORMS = {
  netease: {
    name: "网易云音乐",
    pattern: /music\.163\.com/,
    extractId(url) {
      const match = url.match(/[?&]id=(\d+)/);
      return match ? match[1] : null;
    },
  },
  qq: {
    name: "QQ音乐",
    pattern: /y\.qq\.com/,
    extractId(url) {
      const midMatch =
        url.match(/songDetail\/([a-zA-Z0-9]+)/) ||
        url.match(/songmid=([a-zA-Z0-9]+)/) ||
        url.match(/song\/([a-zA-Z0-9]+)/);

      if (midMatch) return { type: "mid", value: midMatch[1] };

      const idMatch = url.match(/songid=(\d+)/);
      if (idMatch) return { type: "id", value: idMatch[1] };

      return null;
    },
  },
};

function printHelp(code) {
  console.log(`
歌词抓取（CLI）

用法:
  node scripts/fetch_lyrics_cli.js --url "https://music.163.com/song?id=123" --output /abs/path/song-lyrics.txt

参数:
  --url      歌曲链接（网易云/QQ，支持短链接）
  --output   输出 txt 文件路径（建议命名为 {song}-lyrics.txt）

输出文件格式:
  第1行: 歌名
  第2行: 歌手
  空行
  后续: [mm:ss.xx]歌词内容
`);
  process.exit(code);
}

function parseArgs(argv) {
  const args = {};

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "--url") {
      args.url = argv[++i];
    } else if (token === "--output") {
      args.output = argv[++i];
    } else if (token === "-h" || token === "--help") {
      printHelp(0);
    } else {
      console.error(`未知参数: ${token}`);
      printHelp(1);
    }
  }

  if (!args.url || !args.output) {
    console.error("缺少参数: --url 或 --output");
    printHelp(1);
  }

  return args;
}

function requestRaw(url, options = {}) {
  return new Promise((resolve, reject) => {
    const target = new URL(url);
    const client = target.protocol === "https:" ? https : http;

    const req = client.request(
      {
        hostname: target.hostname,
        port: target.port,
        path: `${target.pathname}${target.search}`,
        method: options.method || "GET",
        headers: {
          "User-Agent":
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
          Referer: target.origin,
          ...(options.headers || {}),
        },
      },
      (res) => {
        if (
          res.statusCode >= 300 &&
          res.statusCode < 400 &&
          res.headers.location
        ) {
          resolve({ redirect: res.headers.location, statusCode: res.statusCode });
          return;
        }

        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const raw = Buffer.concat(chunks).toString("utf-8");
          resolve({ raw, statusCode: res.statusCode });
        });
      },
    );

    req.on("error", reject);
    req.end();
  });
}

async function requestJson(url, options = {}) {
  const response = await requestRaw(url, options);
  if (response.redirect) {
    return { redirect: response.redirect };
  }
  try {
    return { data: JSON.parse(response.raw), raw: response.raw };
  } catch {
    return { data: null, raw: response.raw };
  }
}

function isShortLink(url) {
  try {
    const u = new URL(url);
    return SHORT_LINK_DOMAINS.some(
      (domain) => u.hostname === domain || u.hostname.endsWith(`.${domain}`),
    );
  } catch {
    return false;
  }
}

async function resolveShortLink(url) {
  let current = url;

  for (let i = 0; i < 5; i += 1) {
    const response = await requestRaw(current);

    if (response.redirect) {
      current = response.redirect;
      continue;
    }

    const raw = response.raw || "";
    const match =
      raw.match(/location\.href\s*=\s*["']([^"']+)["']/) ||
      raw.match(/window\.location\s*=\s*["']([^"']+)["']/) ||
      raw.match(/<meta[^>]+url=([^"'\s>]+)/i);

    if (match && match[1]) {
      current = match[1];
      continue;
    }

    break;
  }

  return current;
}

function detectPlatform(url) {
  for (const [name, config] of Object.entries(PLATFORMS)) {
    if (config.pattern.test(url)) {
      return { name, config };
    }
  }
  return null;
}

function extractLyricLines(lrcText) {
  const lines = lrcText.split("\n");
  const lyrics = [];

  for (const line of lines) {
    if (/^\[[a-z]+:/i.test(line)) continue;

    const match = line.match(/^(\[\d{2}:\d{2}\.\d{2,3}\])(.*)$/);
    if (match && match[2].trim()) {
      lyrics.push(`${match[1]}${match[2].trim()}`);
    }
  }

  return lyrics;
}

async function fetchFromNetease(songId) {
  const lyricRes = await requestJson(
    `https://music.163.com/api/song/lyric?id=${songId}&lv=1&tv=1`,
  );

  if (!lyricRes.data || lyricRes.data.code !== 200) {
    throw new Error(`网易云歌词接口异常: ${lyricRes.raw || "unknown"}`);
  }

  const lrc = lyricRes.data.lrc && lyricRes.data.lrc.lyric;
  if (!lrc) {
    throw new Error("网易云未返回歌词");
  }

  const detailRes = await requestJson(
    `https://music.163.com/api/song/detail?ids=[${songId}]`,
  );

  const song = detailRes.data && detailRes.data.songs && detailRes.data.songs[0];

  return {
    songName: (song && song.name) || "未知歌曲",
    artist:
      (song && song.artists && song.artists.map((x) => x.name).join("/")) ||
      "未知歌手",
    lrc,
  };
}

async function fetchFromQQ(songIdentifier) {
  let songmid = songIdentifier.value;

  if (songIdentifier.type === "id") {
    const infoRes = await requestJson(
      `https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songid=${songIdentifier.value}&format=json`,
    );

    const item = infoRes.data && infoRes.data.data && infoRes.data.data[0];
    if (!item || !item.mid) {
      throw new Error("QQ音乐: 无法通过 songid 获取 songmid");
    }
    songmid = item.mid;
  }

  const lyricRes = await requestJson(
    `https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg?songmid=${songmid}&format=json&nobase64=1`,
    { headers: { Referer: "https://y.qq.com/" } },
  );

  if (!lyricRes.data) {
    throw new Error("QQ音乐歌词接口返回异常");
  }

  let lrc = lyricRes.data.lyric || "";
  if (lrc && !lrc.includes("[")) {
    try {
      lrc = Buffer.from(lrc, "base64").toString("utf-8");
    } catch {
      // ignore decode errors
    }
  }

  if (!lrc) {
    throw new Error("QQ音乐未返回歌词");
  }

  const detailRes = await requestJson(
    `https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg?songmid=${songmid}&format=json`,
  );

  const item = detailRes.data && detailRes.data.data && detailRes.data.data[0];

  return {
    songName: (item && item.name) || "未知歌曲",
    artist:
      (item && item.singer && item.singer.map((x) => x.name).join("/")) ||
      "未知歌手",
    lrc,
  };
}

async function main() {
  const args = parseArgs(process.argv);
  let songUrl = args.url;
  const outputPath = path.resolve(args.output);

  if (!outputPath.endsWith(".txt")) {
    throw new Error("输出文件必须为 .txt");
  }

  if (isShortLink(songUrl)) {
    console.log("检测到短链接，开始解析...");
    songUrl = await resolveShortLink(songUrl);
    console.log(`短链接解析结果: ${songUrl}`);
  }

  const detected = detectPlatform(songUrl);
  if (!detected) {
    throw new Error("仅支持网易云和QQ音乐链接");
  }

  const songId = detected.config.extractId(songUrl);
  if (!songId) {
    throw new Error("无法从链接中提取歌曲ID");
  }

  console.log(`识别平台: ${detected.config.name}`);

  let result;
  if (detected.name === "netease") {
    result = await fetchFromNetease(songId);
  } else {
    result = await fetchFromQQ(songId);
  }

  const lyricLines = extractLyricLines(result.lrc);
  if (lyricLines.length === 0) {
    throw new Error("歌词为空或未包含时间戳");
  }

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  const content = `${result.songName}\n${result.artist}\n\n${lyricLines.join("\n")}\n`;
  fs.writeFileSync(outputPath, content, "utf-8");

  console.log(
    JSON.stringify(
      {
        success: true,
        url: songUrl,
        songName: result.songName,
        artist: result.artist,
        linesCount: lyricLines.length,
        outputPath,
      },
      null,
      2,
    ),
  );
}

main().catch((err) => {
  console.error(`抓取失败: ${err.message}`);
  process.exit(1);
});
