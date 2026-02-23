---
name: prompt-generator
description: 当用户想生成AI图片但不知道如何写提示词时使用。通过一步步询问确认场景、尺寸、主体、风格等需求，生成完整的AI图片提示词。
---

# AI 图片提示词生成器

当用户想生成AI图片但不知道如何写提示词时，使用本skill。

## 触发条件

用户表达以下意图时：
- "我想生成一张图片"
- "帮我写个AI绘画的提示词"
- "怎么描述能让AI画出xxx"
- "提示词怎么写"
- 或其他想生成AI图片但不知道如何描述的场景

## 工作流程

按以下顺序一步步询问用户，收集必要信息：

### Step 1: 确认使用场景

询问用户图片的用途：
- 头像 / 头像框
- 小红书配图
- 朋友圈
- 壁纸 / 背景图
- 海报 / Banner
- 商品图
- 其他

### Step 2: 确认尺寸偏好

根据场景推荐尺寸并确认：
- 头像：1:1 或圆形
- 小红书：4:5 或 9:16
- 朋友圈：1:1 或 4:3
- 壁纸：16:9 或 9:16
- 海报：16:9 或 4:3
- 商品图：1:1

### Step 3: 确认主体内容

询问用户想生成什么：
- 人物（描述外貌、年龄、性别、服装等）
- 动物
- 景物 / 场景
- 物品
- 抽象概念
- 或用户提供具体描述

### Step 4: 确认风格偏好

提供风格选项供用户选择或描述：
- 写实风格
- 插画 / 漫画风格
- 赛博朋克
- 水彩画
- 宫崎骏风格
- 皮克斯动画
- 中国风 / 国风
- 极简主义
- 用户指定的其他风格

### Step 5: 补充细节（可选）

询问补充信息：
- 色调偏好（暖色/冷色/粉彩/高饱和等）
- 光照偏好（自然光/逆光/霓虹灯/柔光等）
- 构图偏好（特写/全景/正视图/俯视等）
- 背景要求（简洁/复杂/纯色/虚化等）
- 情感/氛围（温馨/浪漫/神秘/酷炫等）

### Step 6: 生成提示词

根据收集的信息，按以下公式组织提示词：

```
[主体描述] + [场景/环境] + [动作/表情] + [风格] + [光照] + [色调] + [构图] + [质量词]
```

根据不同场景添加对应侧重点：
- 头像：添加 `portrait, close-up, simple background`
- 小红书：添加 `vertical, trending on instagram, bold colors`
- 壁纸：添加 `wide view, epic, detailed background`
- 海报：添加 `balanced composition, ample white space`

### Step 7: 输出结果

将生成的完整提示词展示给用户，并说明：
- 提示词的各个部分含义
- 用户可以自行调整的部分
- 建议尝试的变体（可选）

## 提示词公式模板

```
[主体] + [场景] + [动作/姿态] + [风格] + [光照] + [色彩] + [构图] + [质量词]
```

常用质量词参考：
- `high quality, 8k, detailed, masterpiece`
- `beautiful lighting, sharp focus`
- `professional photography`

## 场景对应侧重点

| 场景 | 尺寸 | 侧重点提示词 |
|------|------|--------------|
| 头像 | 1:1 | portrait, close-up, simple background |
| 小红书 | 4:5 / 9:16 | vertical, trending, bold colors |
| 朋友圈 | 1:1 / 4:3 | clean, simple |
| 壁纸 | 16:9 / 9:16 | wide view, epic, detailed |
| 海报 | 多尺寸 | balanced composition, white space |
| 商品图 | 1:1 | clean background, product focus |

## 输出示例

用户选择：头像 + 人物少女 + 赛博朋克风格

生成的提示词：
> 一位赛博朋克风格的白发少女，机械义眼，城市霓虹灯背景，街道下雨场景，cool tone, neon lighting, wet street, reflections, hyper-realistic, 8k, detailed, masterpiece, portrait, close-up, simple background

## 注意事项

- 询问时一次只问1-2个问题，避免信息过载
- 用户无法描述主体时，提供示例帮助引导
- 风格不确定时，列出3-5个选项供选择
- 生成后询问用户是否需要调整
