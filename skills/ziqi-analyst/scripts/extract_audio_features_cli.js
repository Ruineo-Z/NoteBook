#!/usr/bin/env node

/**
 * 音频特征提取（Codex/CLI 版）
 *
 * 目标：替代 PromptX 的 audio-feature-extractor 运行时依赖。
 * 输出：
 *   - {song}.features.csv
 *   - {song}.features.meta.json
 */

const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const MusicTempo = require("music-tempo");

function parseArgs(argv) {
  const args = {
    samplingInterval: 5,
    sampleRate: 44100,
  };

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];

    if (token === "--audio") {
      args.audio = argv[++i];
    } else if (token === "--out-dir") {
      args.outDir = argv[++i];
    } else if (token === "--output-prefix") {
      args.outputPrefix = argv[++i];
    } else if (token === "--sampling-interval") {
      args.samplingInterval = Number(argv[++i]);
    } else if (token === "--sample-rate") {
      args.sampleRate = Number(argv[++i]);
    } else if (token === "-h" || token === "--help") {
      printHelp(0);
    } else {
      console.error(`未知参数: ${token}`);
      printHelp(1);
    }
  }

  if (!args.audio) {
    console.error("缺少参数: --audio");
    printHelp(1);
  }

  if (!Number.isFinite(args.samplingInterval) || args.samplingInterval <= 0) {
    console.error("--sampling-interval 必须为正数");
    process.exit(1);
  }

  if (!Number.isFinite(args.sampleRate) || args.sampleRate < 8000) {
    console.error("--sample-rate 不合法");
    process.exit(1);
  }

  return args;
}

function printHelp(code) {
  console.log(`
音频特征提取（CLI）

用法:
  node scripts/extract_audio_features_cli.js --audio /abs/path/song.mp3

可选参数:
  --out-dir /abs/path              输出目录，默认与音频同目录
  --output-prefix song             输出前缀，默认用音频文件名
  --sampling-interval 5            采样间隔秒数，默认 5
  --sample-rate 44100              ffmpeg 解码采样率，默认 44100

输出文件:
  {prefix}.features.csv
  {prefix}.features.meta.json
`);
  process.exit(code);
}

function formatDuration(durationSec) {
  const whole = Math.max(0, Math.floor(durationSec));
  const mm = Math.floor(whole / 60);
  const ss = whole % 60;
  return `${String(mm).padStart(2, "0")}:${String(ss).padStart(2, "0")}`;
}

function decodeAudioToFloat32(audioPath, sampleRate) {
  return new Promise((resolve, reject) => {
    const ffmpeg = spawn("ffmpeg", [
      "-i",
      audioPath,
      "-f",
      "f32le",
      "-acodec",
      "pcm_f32le",
      "-ar",
      String(sampleRate),
      "-ac",
      "1",
      "-",
    ]);

    const outChunks = [];
    let stderr = "";

    ffmpeg.stdout.on("data", (chunk) => outChunks.push(chunk));
    ffmpeg.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    ffmpeg.on("error", (err) => {
      reject(new Error(`ffmpeg 启动失败: ${err.message}`));
    });

    ffmpeg.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`ffmpeg 失败（code=${code}）: ${stderr.slice(-400)}`));
        return;
      }

      const buffer = Buffer.concat(outChunks);
      const ab = buffer.buffer.slice(
        buffer.byteOffset,
        buffer.byteOffset + buffer.byteLength,
      );
      resolve(new Float32Array(ab));
    });
  });
}

function computeRmsSeries(samples, sampleRate, samplingInterval) {
  const totalDuration = samples.length / sampleRate;
  const rows = [];

  for (let t = 0; t < totalDuration; t += samplingInterval) {
    const start = Math.floor(t * sampleRate);
    const end = Math.min(
      samples.length,
      Math.floor((t + samplingInterval) * sampleRate),
    );

    let sumSq = 0;
    for (let i = start; i < end; i += 1) {
      const v = samples[i];
      sumSq += v * v;
    }

    const n = Math.max(1, end - start);
    const rms = Math.sqrt(sumSq / n);

    rows.push({
      time: Number(t.toFixed(3)),
      rms: Number(rms.toFixed(8)),
    });
  }

  return rows;
}

function detectBpm(samples, sampleRate) {
  const maxSeconds = 180;
  const maxSamples = sampleRate * maxSeconds;
  const clipped = samples.length > maxSamples ? samples.slice(0, maxSamples) : samples;

  try {
    const mt = new MusicTempo(clipped);
    if (!Number.isFinite(mt.tempo) || mt.tempo <= 0) {
      return null;
    }

    return {
      bpm: Number(mt.tempo.toFixed(2)),
      method: "music-tempo",
      beats: Array.isArray(mt.beats) ? mt.beats.length : 0,
      confidence: null,
    };
  } catch (err) {
    return {
      bpm: null,
      method: "music-tempo",
      beats: 0,
      confidence: null,
      error: err.message,
    };
  }
}

function writeOutputs({
  audioPath,
  outDir,
  prefix,
  sampleRate,
  samplingInterval,
  rows,
  bpm,
  sampleCount,
}) {
  fs.mkdirSync(outDir, { recursive: true });

  const csvPath = path.join(outDir, `${prefix}.features.csv`);
  const metaPath = path.join(outDir, `${prefix}.features.meta.json`);

  const csvLines = ["time,rms"];
  for (const row of rows) {
    csvLines.push(`${row.time},${row.rms}`);
  }
  fs.writeFileSync(csvPath, `${csvLines.join("\n")}\n`, "utf-8");

  const avgRms =
    rows.length > 0
      ? Number((rows.reduce((acc, x) => acc + x.rms, 0) / rows.length).toFixed(8))
      : null;

  const duration = sampleCount / sampleRate;

  const meta = {
    originalFile: audioPath,
    extractedAt: new Date().toISOString(),
    audioInfo: {
      sampleRate,
      duration,
      durationFormatted: formatDuration(duration),
      numberOfChannels: 1,
      length: sampleCount,
    },
    bpm,
    averageFeatures: {
      rms: avgRms,
    },
    metadata: {
      samplingInterval,
      samplingIntervalUnit: "seconds",
      dataPoints: rows.length,
      generator: "extract_audio_features_cli",
    },
  };

  fs.writeFileSync(metaPath, `${JSON.stringify(meta, null, 2)}\n`, "utf-8");

  return { csvPath, metaPath, duration, avgRms };
}

async function main() {
  const args = parseArgs(process.argv);

  const audioPath = path.resolve(args.audio);
  if (!fs.existsSync(audioPath)) {
    throw new Error(`音频文件不存在: ${audioPath}`);
  }

  const ext = path.extname(audioPath);
  const stem = path.basename(audioPath, ext);
  const outDir = path.resolve(args.outDir || path.dirname(audioPath));
  const prefix = args.outputPrefix || stem;

  console.log(`[1/3] 解码音频: ${audioPath}`);
  const samples = await decodeAudioToFloat32(audioPath, args.sampleRate);

  console.log(`[2/3] 计算 RMS 时序（interval=${args.samplingInterval}s）`);
  const rows = computeRmsSeries(samples, args.sampleRate, args.samplingInterval);

  console.log("[3/3] 估计 BPM");
  const bpm = detectBpm(samples, args.sampleRate);

  const { csvPath, metaPath } = writeOutputs({
    audioPath,
    outDir,
    prefix,
    sampleRate: args.sampleRate,
    samplingInterval: args.samplingInterval,
    rows,
    bpm,
    sampleCount: samples.length,
  });

  const result = {
    success: true,
    audioPath,
    featuresFile: csvPath,
    metaFile: metaPath,
    samplingInterval: args.samplingInterval,
    bpm,
    rows: rows.length,
  };

  console.log(JSON.stringify(result, null, 2));
}

main().catch((err) => {
  console.error(`提取失败: ${err.message}`);
  process.exit(1);
});
