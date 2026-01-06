<script setup lang="ts">
/**
 * Cyberpunk Spirit Tree - 赛博灵魂树
 * 程序化生成的粒子树 + 数字波浪地面 + Bloom 辉光
 */
import { ref, onMounted, onUnmounted } from 'vue'
import * as THREE from 'three'
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js'
import { RenderPass } from 'three/examples/jsm/postprocessing/RenderPass.js'
import { UnrealBloomPass } from 'three/examples/jsm/postprocessing/UnrealBloomPass.js'

const containerRef = ref<HTMLDivElement>()

// 滚动淡出效果
const scrollProgress = ref(0)

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let composer: EffectComposer
let animationId: number
let time = 0

// 粒子系统
let treeParticles: THREE.Points
let leafParticles: THREE.Points  // 叶子发光点
let dustParticles: THREE.Points
let groundParticles: THREE.Points  // 能量汇聚粒子
let groundWaveParticles: THREE.Points  // 地面波动粒子
let rootGlow: THREE.Mesh  // 根部能量光晕
let bridgeLines: THREE.Points  // 横向连接粒子线

// 树枝数据（用于生成粒子）
const branches: { start: THREE.Vector3; end: THREE.Vector3; level: number }[] = []

// ========== 1. 程序化生成树结构（按层级设计） ==========
function generateTreeStructure() {
  branches.length = 0
  
  // === 第1级：主干（老树蜿蜒效果，分多段弯曲） ===
  // 老树主干不是笔直的，而是有自然的弯曲和扭曲
  const trunkSegments = 8  // 分成8段来模拟弯曲
  const trunkPoints: THREE.Vector3[] = []
  
  // 生成蜿蜒的主干路径点
  for (let i = 0; i <= trunkSegments; i++) {
    const t = i / trunkSegments
    const y = -2.5 + t * 4.0  // 从 -2.5 到 1.5
    
    // 多层次的自然弯曲
    // 主弯曲 - 大幅度的S形弯曲（像老树被风吹歪）
    const mainBendX = Math.sin(t * Math.PI * 1.2 + 0.5) * 0.4
    const mainBendZ = Math.cos(t * Math.PI * 0.8 + 0.3) * 0.25
    
    // 次级扭曲 - 中等频率的蜿蜒
    const twistX = Math.sin(t * Math.PI * 3 + 1.2) * 0.15
    const twistZ = Math.cos(t * Math.PI * 2.5 + 0.8) * 0.12
    
    // 细节抖动 - 高频的不规则感
    const noiseX = (Math.random() - 0.5) * 0.08
    const noiseZ = (Math.random() - 0.5) * 0.08
    
    trunkPoints.push(new THREE.Vector3(
      mainBendX + twistX + noiseX,
      y,
      mainBendZ + twistZ + noiseZ
    ))
  }
  
  // 将主干路径点连接成分段
  for (let i = 0; i < trunkSegments; i++) {
    branches.push({ 
      start: trunkPoints[i].clone(), 
      end: trunkPoints[i + 1].clone(), 
      level: 0 
    })
  }
  
  // 主干顶端位置（用于后续分枝）
  const trunkEnd = trunkPoints[trunkPoints.length - 1]
  
  // === 第2级：主分枝（6根，从主干顶端向外展开） ===
  const mainBranchCount = 6
  const mainBranches: { start: THREE.Vector3; end: THREE.Vector3 }[] = []
  
  for (let i = 0; i < mainBranchCount; i++) {
    const theta = (i / mainBranchCount) * Math.PI * 2 + Math.random() * 0.2
    const length = 2.8 + Math.random() * 0.8
    const upward = 0.3 + Math.random() * 0.25  // 稍微向上
    
    const dir = new THREE.Vector3(
      Math.cos(theta),
      upward,
      Math.sin(theta)
    ).normalize()
    
    const end = trunkEnd.clone().add(dir.multiplyScalar(length))
    branches.push({ start: trunkEnd.clone(), end, level: 1 })
    mainBranches.push({ start: trunkEnd.clone(), end })
  }
  
  // === 第3级：侧枝（每个主分枝分出5-8根，总共约35根） ===
  const sideBranches: { start: THREE.Vector3; end: THREE.Vector3 }[] = []
  
  mainBranches.forEach((mb) => {
    const sideCount = 5 + Math.floor(Math.random() * 4)  // 5-8根
    const mbDir = mb.end.clone().sub(mb.start).normalize()
    
    for (let i = 0; i < sideCount; i++) {
      // 沿主分枝的不同位置分出
      const t = 0.3 + (i / sideCount) * 0.6
      const branchPoint = mb.start.clone().lerp(mb.end, t)
      
      // 侧枝方向：在主分枝方向基础上偏转
      const sideAngle = (Math.random() - 0.5) * Math.PI * 0.8
      const length = 1.5 + Math.random() * 1.0
      
      const sideDir = new THREE.Vector3(
        mbDir.x * Math.cos(sideAngle) - mbDir.z * Math.sin(sideAngle),
        0.15 + Math.random() * 0.2,
        mbDir.x * Math.sin(sideAngle) + mbDir.z * Math.cos(sideAngle)
      ).normalize()
      
      const end = branchPoint.clone().add(sideDir.multiplyScalar(length))
      branches.push({ start: branchPoint, end, level: 2 })
      sideBranches.push({ start: branchPoint, end })
    }
  })
  
  // === 第4级：细枝/末梢（每个侧枝分出5-12根，总共约250根） ===
  sideBranches.forEach(sb => {
    const twigCount = 5 + Math.floor(Math.random() * 8)  // 5-12根
    const sbDir = sb.end.clone().sub(sb.start).normalize()
    
    for (let i = 0; i < twigCount; i++) {
      const t = 0.4 + (i / twigCount) * 0.5
      const branchPoint = sb.start.clone().lerp(sb.end, t)
      
      const twigAngle = (Math.random() - 0.5) * Math.PI
      const length = 0.6 + Math.random() * 0.8
      
      const twigDir = new THREE.Vector3(
        sbDir.x * Math.cos(twigAngle) - sbDir.z * Math.sin(twigAngle) + (Math.random() - 0.5) * 0.3,
        0.1 + Math.random() * 0.15,
        sbDir.x * Math.sin(twigAngle) + sbDir.z * Math.cos(twigAngle) + (Math.random() - 0.5) * 0.3
      ).normalize()
      
      const end = branchPoint.clone().add(twigDir.multiplyScalar(length))
      branches.push({ start: branchPoint, end, level: 3 })
    }
  })
}

// ========== 2. 根据树枝生成粒子 ==========
function createTreeParticles(): THREE.Points {
  // 先生成树枝结构
  generateTreeStructure()

  // 统计需要的粒子数（沿枝条 + 末端簇团）
  let totalParticles = 0
  branches.forEach(b => {
    const len = b.start.distanceTo(b.end)
    // 主干非常密集和粗壮，分枝逐级递减
    const density = b.level === 0 ? 350 : (b.level === 1 ? 100 : (b.level === 2 ? 45 : 20))
    totalParticles += Math.ceil(len * density)
    // 末端叶团
    if (b.level === 3) totalParticles += 8
  })

  const positions = new Float32Array(totalParticles * 3)
  const colors = new Float32Array(totalParticles * 3)
  const sizes = new Float32Array(totalParticles)
  const seeds = new Float32Array(totalParticles)

  let idx = 0
  // 色彩微调：树干青白色，树冠深蓝色
  const colorTrunk = new THREE.Color(0x88ffff)  // 青白色（主干最亮）
  const colorBranch = new THREE.Color(0x00ddff) // 青色（分枝）
  const colorLeaf = new THREE.Color(0x0055aa)   // 深蓝色（树冠末端）

  branches.forEach(b => {
    const len = b.start.distanceTo(b.end)
    // 主干非常密集，分枝逐级递减
    const density = b.level === 0 ? 350 : (b.level === 1 ? 100 : (b.level === 2 ? 45 : 20))
    const count = Math.ceil(len * density)

    // 沿枝条生成粒子
    for (let i = 0; i < count; i++) {
      const t = i / count
      const pos = b.start.clone().lerp(b.end, t)
      // 主干非常粗壮，分枝逐渐变细
      const spread = b.level === 0 ? 0.45 : (b.level === 1 ? 0.18 : (b.level === 2 ? 0.08 : 0.04))
      pos.x += (Math.random() - 0.5) * spread
      pos.y += (Math.random() - 0.5) * spread * 0.4
      pos.z += (Math.random() - 0.5) * spread

      positions[idx * 3] = pos.x
      positions[idx * 3 + 1] = pos.y
      positions[idx * 3 + 2] = pos.z

      // 颜色梯度：主干青白 → 分枝青色 → 末端深蓝
      let color: THREE.Color
      if (b.level === 0) {
        color = colorTrunk.clone().lerp(colorBranch, t * 0.3)
      } else if (b.level === 1) {
        color = colorBranch.clone().lerp(colorLeaf, t * 0.4)
      } else {
        color = colorBranch.clone().lerp(colorLeaf, 0.3 + t * 0.5 + Math.random() * 0.2)
      }
      colors[idx * 3] = color.r
      colors[idx * 3 + 1] = color.g
      colors[idx * 3 + 2] = color.b

      // 主干粒子更大
      sizes[idx] = b.level === 0 ? 5.5 : (b.level === 1 ? 3.8 : (b.level === 2 ? 2.5 : 1.8))
      seeds[idx] = Math.random()
      idx++
    }

    // 末端叶团（细枝末梢的小光点）- 深蓝色
    if (b.level === 3) {
      for (let i = 0; i < 8; i++) {
        const r = 0.2 + Math.random() * 0.4
        const theta = Math.random() * Math.PI * 2
        const phi = Math.random() * Math.PI * 0.4

        positions[idx * 3] = b.end.x + Math.sin(phi) * Math.cos(theta) * r
        positions[idx * 3 + 1] = b.end.y + Math.cos(phi) * r * 0.3 + Math.random() * 0.15
        positions[idx * 3 + 2] = b.end.z + Math.sin(phi) * Math.sin(theta) * r

        // 叶团使用深蓝+随机变化
        const color = colorLeaf.clone().lerp(colorBranch, Math.random() * 0.3)
        colors[idx * 3] = color.r
        colors[idx * 3 + 1] = color.g
        colors[idx * 3 + 2] = color.b

        sizes[idx] = 1.2 + Math.random() * 1.5
        seeds[idx] = Math.random()
        idx++
      }
    }
  })

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
  geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1))

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uPixelRatio: { value: Math.min(window.devicePixelRatio, 2) }
    },
    vertexShader: `
      uniform float uTime;
      uniform float uPixelRatio;
      attribute float size;
      attribute float aSeed;
      varying vec3 vColor;
      varying float vAlpha;

      void main() {
        vColor = color;
        
        // 轻微漂浮动画
        vec3 pos = position;
        float wave = sin(uTime * (1.0 + aSeed) + aSeed * 20.0) * 0.02;
        pos.y += wave;
        pos.x += cos(uTime * 0.8 + aSeed * 15.0) * 0.015;
        
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = size * uPixelRatio * (8.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
        
        // 闪烁
        vAlpha = 0.7 + 0.3 * sin(uTime * (2.0 + aSeed * 3.0) + aSeed * 50.0);
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      varying float vAlpha;

      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        
        // 柔和发光边缘
        float glow = 1.0 - smoothstep(0.0, 0.5, d);
        vec3 finalColor = vColor * (1.0 + glow * 0.5);
        
        gl_FragColor = vec4(finalColor, glow * vAlpha);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    vertexColors: true
  })

  return new THREE.Points(geometry, material)
}

// ========== 3. 叶子发光粒子（5000个模糊大点） ==========
function createLeafParticles(): THREE.Points {
  const count = 5000
  const positions = new Float32Array(count * 3)
  const seeds = new Float32Array(count)
  
  // 收集所有末端位置（level 2 和 level 3 的末端）
  const tips: THREE.Vector3[] = []
  branches.forEach(b => {
    if (b.level >= 2) {
      tips.push(b.end.clone())
    }
  })
  
  for (let i = 0; i < count; i++) {
    // 随机选择一个末端作为中心
    const tip = tips[Math.floor(Math.random() * tips.length)]
    
    // 在末端周围随机分布（更立体的球形，顶部更高）
    const r = 0.3 + Math.random() * 1.4
    const theta = Math.random() * Math.PI * 2
    const phi = Math.random() * Math.PI * 0.8  // 偏向上方
    
    // Y轴增加高度差，顶部更高，形成立体球形
    const heightBoost = Math.pow(Math.random(), 0.7) * 1.2  // 顶部粒子更高
    
    positions[i * 3] = tip.x + Math.sin(phi) * Math.cos(theta) * r
    positions[i * 3 + 1] = tip.y + Math.cos(phi) * r * 0.8 + heightBoost
    positions[i * 3 + 2] = tip.z + Math.sin(phi) * Math.sin(theta) * r
    seeds[i] = Math.random()
  }
  
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1))
  
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 }
    },
    vertexShader: `
      uniform float uTime;
      attribute float aSeed;
      varying float vAlpha;
      varying float vSeed;
      
      void main() {
        vSeed = aSeed;
        vec3 pos = position;
        
        // 轻微随机漂浮
        pos.x += sin(uTime * (0.5 + aSeed * 0.8) + aSeed * 30.0) * 0.1;
        pos.y += cos(uTime * (0.4 + aSeed * 0.6) + aSeed * 20.0) * 0.08;
        pos.z += sin(uTime * (0.6 + aSeed * 0.5) + aSeed * 25.0) * 0.1;
        
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        
        // 呼吸律动：大小随时间缓慢波动
        float breathe = 0.85 + 0.15 * sin(uTime * 0.8 + aSeed * 6.28);
        gl_PointSize = (10.0 + aSeed * 8.0) * breathe * (10.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
        
        // 呼吸感：亮度也随之波动
        float breatheAlpha = 0.8 + 0.2 * sin(uTime * 0.8 + aSeed * 6.28);
        float flicker = sin(uTime * (1.0 + aSeed * 1.5) + aSeed * 40.0);
        vAlpha = (0.15 + 0.15 * flicker) * breatheAlpha;
      }
    `,
    fragmentShader: `
      varying float vAlpha;
      varying float vSeed;
      
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        
        // 非常柔和的高斯模糊边缘（边缘雾化）
        float glow = exp(-d * d * 6.0);
        
        // 色彩微调：深蓝渐变到青色
        vec3 colorDeep = vec3(0.0, 0.35, 0.7);  // 深蓝
        vec3 colorBright = vec3(0.3, 0.85, 1.0); // 亮青
        vec3 color = mix(colorDeep, colorBright, vAlpha * 1.5);
        
        gl_FragColor = vec4(color, glow * vAlpha * 0.9);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  return new THREE.Points(geometry, material)
}

// ========== 4a. 地面波动粒子海（保持原有效果） ==========
function createGroundWaveParticles(): THREE.Points {
  const count = 8000
  const positions = new Float32Array(count * 3)
  const seeds = new Float32Array(count)
  
  for (let i = 0; i < count; i++) {
    const r = 1.5 + Math.random() * 14
    const theta = Math.random() * Math.PI * 2
    positions[i * 3] = Math.cos(theta) * r
    positions[i * 3 + 1] = 0
    positions[i * 3 + 2] = Math.sin(theta) * r
    seeds[i] = Math.random()
  }
  
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1))
  
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 }
    },
    vertexShader: `
      uniform float uTime;
      attribute float aSeed;
      varying float vAlpha;
      
      void main() {
        vec3 pos = position;
        float r = length(pos.xz);
        float angle = atan(pos.z, pos.x);
        
        // 向心波动
        float wave = sin(r * 1.2 - uTime * 0.8 + aSeed * 3.0) * 0.15;
        wave += sin(r * 0.6 + uTime * 0.3) * 0.1;
        pos.y = wave;
        
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = (1.5 + aSeed * 1.0) * (6.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
        
        // 中心更亮
        float distFade = smoothstep(15.0, 2.0, r);
        vAlpha = (0.15 + 0.1 * sin(uTime * 1.5 + aSeed * 10.0)) * distFade;
      }
    `,
    fragmentShader: `
      varying float vAlpha;
      
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        
        float glow = 1.0 - smoothstep(0.0, 0.5, d);
        vec3 color = vec3(0.15, 0.5, 0.8);
        
        gl_FragColor = vec4(color, glow * vAlpha);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  return new THREE.Points(geometry, material)
}

// ========== 4b. 能量汇聚粒子（向心流动 + 沿树干攀爬） ==========
function createParticleSea(): THREE.Points {
  const count = 6000  // 汇聚粒子数量（减少一些）
  const veinCount = 32  // 能量脉络数量
  
  // 粒子属性
  const positions = new Float32Array(count * 3)
  const seeds = new Float32Array(count)
  const pathIndices = new Float32Array(count)
  const phases = new Float32Array(count)
  
  for (let i = 0; i < count; i++) {
    pathIndices[i] = Math.floor(Math.random() * veinCount)
    phases[i] = Math.random()
    seeds[i] = Math.random()
    positions[i * 3] = 0
    positions[i * 3 + 1] = 0
    positions[i * 3 + 2] = 0
  }
  
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1))
  geometry.setAttribute('aPathIndex', new THREE.BufferAttribute(pathIndices, 1))
  geometry.setAttribute('aPhase', new THREE.BufferAttribute(phases, 1))
  
  // 树缩放比例
  const treeScale = 0.6
  
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uVeinCount: { value: veinCount },
      uTreeScale: { value: treeScale }
    },
    vertexShader: `
      uniform float uTime;
      uniform float uVeinCount;
      uniform float uTreeScale;
      
      attribute float aSeed;
      attribute float aPathIndex;
      attribute float aPhase;
      
      varying float vAlpha;
      varying float vPhase;
      varying vec2 vStretch;
      
      // 地面脉络路径（从远处蜿蜒到中心）
      vec3 getGroundPath(float pathIdx, float t) {
        float baseAngle = (pathIdx / uVeinCount) * 6.28318 + sin(pathIdx * 0.7) * 0.3;
        float r = 12.0 * (1.0 - t);  // 从远到近
        
        // 蜿蜒效果
        float waveAngle = baseAngle + sin(t * 6.28318 + pathIdx * 0.5) * 0.3;
        float bendOffset = sin(t * 9.42 + pathIdx) * 0.5 * (1.0 - t);
        
        return vec3(
          cos(waveAngle) * r + bendOffset * sin(waveAngle),
          sin(t * 3.14159 + aSeed * 2.0) * 0.1,  // 轻微起伏
          sin(waveAngle) * r - bendOffset * cos(waveAngle)
        );
      }
      
      // 树干攀爬路径（与树粒子系统完全对齐）
      vec3 getTrunkPath(float t, float angleOffset) {
        // 树干本地 y 范围：-2.5 到 1.5（共4单位）
        // 树整体缩放 0.6，世界坐标 y = 本地 y * 0.6
        // 树干底部世界 y = -2.5 * 0.6 = -1.5
        // 树干顶部世界 y = 1.5 * 0.6 = 0.9
        // 地面粒子系统在世界 y = -1.5（与树干底部对齐）
        // 所以本地 y 从 0 到 2.4
        float localY = t * 2.4;
        
        // 模拟树干的弯曲（与generateTreeStructure一致，但也要缩放）
        float bendX = (sin(t * 3.77 + 0.5) * 0.4 + sin(t * 9.42 + 1.2) * 0.15) * uTreeScale;
        float bendZ = (cos(t * 2.51 + 0.3) * 0.25 + cos(t * 7.85 + 0.8) * 0.12) * uTreeScale;
        
        // 螺旋效果（缩小半径，紧贴树干）
        float spiralRadius = (0.15 + (1.0 - t) * 0.12) * uTreeScale;
        float spiralAngle = angleOffset + t * 4.0;
        
        return vec3(
          bendX + cos(spiralAngle) * spiralRadius,
          localY,
          bendZ + sin(spiralAngle) * spiralRadius
        );
      }
      
      void main() {
        // 生命周期：18-25秒一个完整循环（非常慢的流动）
        float cycleTime = 18.0 + aSeed * 7.0;
        float lifeProgress = fract((uTime + aPhase * cycleTime) / cycleTime);
        
        vec3 pos;
        float alpha = 1.0;
        vec2 stretch = vec2(1.0, 1.0);
        
        // 角度偏移（基于路径索引）
        float angleOffset = (aPathIndex / uVeinCount) * 6.28318;
        
        // === 阶段划分 ===
        // 0.0 - 0.60: 地面汇聚（更长时间）
        // 0.60 - 0.65: 过渡（进入树根）
        // 0.65 - 0.92: 沿树干攀爬
        // 0.92 - 1.0: 消散融入树冠
        
        if (lifeProgress < 0.60) {
          // === 阶段A: 地面脉络汇聚 ===
          float groundT = lifeProgress / 0.60;
          pos = getGroundPath(aPathIndex, groundT);
          
          // 拖尾
          stretch = vec2(1.8 + groundT * 0.5, 0.6);
          
          // 接近中心时变亮
          float dist = length(pos.xz);
          alpha = smoothstep(12.0, 0.5, dist) * (0.4 + 0.25 * sin(uTime * 3.0 + aSeed * 6.0));
          
        } else if (lifeProgress < 0.65) {
          // === 过渡阶段: 进入树根 ===
          float transT = (lifeProgress - 0.60) / 0.05;
          
          // 从地面终点平滑过渡到树干起点
          vec3 groundEnd = getGroundPath(aPathIndex, 1.0);
          groundEnd.y = 0.0;
          vec3 trunkStart = getTrunkPath(0.0, angleOffset);
          
          pos = mix(groundEnd, trunkStart, smoothstep(0.0, 1.0, transT));
          
          stretch = vec2(1.0, 1.2);
          alpha = 0.7 + 0.2 * transT;
          
        } else if (lifeProgress < 0.92) {
          // === 阶段B: 沿树干攀爬 ===
          float climbT = (lifeProgress - 0.65) / 0.27;
          pos = getTrunkPath(climbT, angleOffset);
          
          // 垂直方向微拉长
          stretch = vec2(0.7, 1.3);
          
          // 攀爬时明亮
          alpha = 0.6 + 0.2 * sin(climbT * 3.14159);
          
        } else {
          // === 阶段C: 消散融入树冠 ===
          float fadeT = (lifeProgress - 0.92) / 0.08;
          
          // 从树干顶部向外扩散
          vec3 trunkTop = getTrunkPath(1.0, angleOffset);
          float expandRadius = fadeT * 0.8 * uTreeScale;
          float expandAngle = angleOffset + fadeT * 2.5 + aSeed * 1.5;
          
          pos = trunkTop + vec3(
            cos(expandAngle) * expandRadius,
            fadeT * 0.5,
            sin(expandAngle) * expandRadius
          );
          
          stretch = vec2(1.0, 1.0);
          alpha = (1.0 - fadeT) * 0.5;
        }
        
        vAlpha = alpha;
        vPhase = lifeProgress;
        vStretch = stretch;
        
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        
        // 粒子大小：更小一些
        float baseSize = lifeProgress < 0.60 ? 1.5 : 2.0;
        gl_PointSize = (baseSize + aSeed * 0.8) * (7.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      varying float vAlpha;
      varying float vPhase;
      varying vec2 vStretch;
      
      void main() {
        // 拖尾效果
        vec2 uv = gl_PointCoord - vec2(0.5);
        uv.x *= vStretch.x;
        uv.y *= vStretch.y;
        float d = length(uv);
        
        if (d > 0.5) discard;
        
        float glow = 1.0 - smoothstep(0.0, 0.5, d);
        
        // 颜色渐变
        vec3 colorGround = vec3(0.0, 0.5, 0.8);
        vec3 colorClimb = vec3(0.3, 0.9, 1.0);
        vec3 colorFade = vec3(0.5, 0.85, 1.0);
        
        vec3 color;
        if (vPhase < 0.60) {
          color = mix(colorGround, colorClimb, vPhase / 0.60);
        } else if (vPhase < 0.92) {
          color = colorClimb;
        } else {
          color = mix(colorClimb, colorFade, (vPhase - 0.92) / 0.08);
        }
        
        gl_FragColor = vec4(color, glow * vAlpha);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  return new THREE.Points(geometry, material)
}


// ========== 4. 能量尘埃粒子 ==========
function createDustParticles(): THREE.Points {
  const count = 2000
  const positions = new Float32Array(count * 3)
  const seeds = new Float32Array(count)

  for (let i = 0; i < count; i++) {
    // 在树周围的空间分布
    const r = 2 + Math.random() * 12
    const theta = Math.random() * Math.PI * 2
    const y = -2 + Math.random() * 12

    positions[i * 3] = Math.cos(theta) * r
    positions[i * 3 + 1] = y
    positions[i * 3 + 2] = Math.sin(theta) * r
    seeds[i] = Math.random()
  }

  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1))

  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 }
    },
    vertexShader: `
      uniform float uTime;
      attribute float aSeed;
      varying float vAlpha;

      void main() {
        vec3 pos = position;
        
        // 螺旋上升 + 漂浮
        float angle = uTime * (0.1 + aSeed * 0.15) + aSeed * 20.0;
        float r = length(pos.xz);
        pos.x = cos(angle) * r;
        pos.z = sin(angle) * r;
        pos.y += sin(uTime * 0.5 + aSeed * 10.0) * 0.3;
        
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = (2.0 + aSeed * 2.0) * (6.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
        
        vAlpha = 0.3 + 0.4 * sin(uTime * (1.5 + aSeed * 2.0) + aSeed * 30.0);
      }
    `,
    fragmentShader: `
      varying float vAlpha;

      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        
        float glow = 1.0 - d * 2.0;
        vec3 color = vec3(0.3, 0.8, 1.0);
        
        gl_FragColor = vec4(color, glow * vAlpha);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })

  return new THREE.Points(geometry, material)
}

// ========== 6. 根部能量光晕 ==========
function createRootGlow(): THREE.Mesh {
  // 使用圆形平面 + 发光材质
  const geometry = new THREE.CircleGeometry(2.5, 64)
  
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 }
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float uTime;
      varying vec2 vUv;
      
      void main() {
        vec2 center = vUv - vec2(0.5);
        float dist = length(center) * 2.0;
        float angle = atan(center.y, center.x);
        
        // 中心最亮，向外衰减（能量光晕）
        float glow = 1.0 - smoothstep(0.0, 1.0, dist);
        glow = pow(glow, 1.5);
        
        // 向外扩散的能量线条（8条纤细射线）
        float rays = 0.0;
        for (int i = 0; i < 8; i++) {
          float rayAngle = float(i) * 0.785398 + uTime * 0.3;  // 旋转
          float rayDiff = abs(mod(angle - rayAngle + 3.14159, 6.28318) - 3.14159);
          float ray = smoothstep(0.15, 0.0, rayDiff) * smoothstep(1.0, 0.3, dist);
          ray *= 0.3 + 0.7 * sin(dist * 8.0 - uTime * 3.0);  // 向外流动
          rays += ray * 0.15;
        }
        
        // 呼吸脉动
        float pulse = 0.8 + 0.2 * sin(uTime * 1.5);
        
        // 青蓝色光晕
        vec3 colorCore = vec3(0.4, 1.0, 1.0);
        vec3 colorEdge = vec3(0.0, 0.4, 0.8);
        vec3 color = mix(colorEdge, colorCore, glow + rays);
        
        gl_FragColor = vec4(color, (glow * 0.5 + rays) * pulse);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide
  })
  
  const mesh = new THREE.Mesh(geometry, material)
  mesh.rotation.x = -Math.PI / 2  // 水平放置
  return mesh
}

// ========== 7. 飘散粒子（从树冠飘向左侧，视觉融合） ==========
function createBridgeLines(): THREE.Points {
  const count = 4000
  const positions = new Float32Array(count * 3)
  const seeds = new Float32Array(count)
  
  for (let i = 0; i < count; i++) {
    // 从树冠区域向左飘散
    const x = -12 + Math.random() * 18  // 覆盖左侧文字到右侧树
    const y = -1 + Math.random() * 8    // 主要在中上部
    const z = -4 + Math.random() * 8
    
    positions[i * 3] = x
    positions[i * 3 + 1] = y
    positions[i * 3 + 2] = z
    seeds[i] = Math.random()
  }
  
  const geometry = new THREE.BufferGeometry()
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('aSeed', new THREE.BufferAttribute(seeds, 1))
  
  const material = new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 }
    },
    vertexShader: `
      uniform float uTime;
      attribute float aSeed;
      varying float vAlpha;
      
      void main() {
        vec3 pos = position;
        
        // 缓慢向左飘动
        pos.x -= uTime * 0.15 + aSeed * 0.5;
        pos.x = mod(pos.x + 12.0, 30.0) - 12.0;
        
        // 轻微上下浮动
        pos.y += sin(uTime * 0.5 + aSeed * 20.0) * 0.3;
        
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = (1.5 + aSeed * 2.0) * (6.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
        
        // 右侧靠近树更亮，左侧极淡
        float xFade = smoothstep(-12.0, 6.0, pos.x);
        float breathe = 0.7 + 0.3 * sin(uTime * 0.6 + aSeed * 10.0);
        vAlpha = 0.02 + 0.08 * xFade * breathe;
      }
    `,
    fragmentShader: `
      varying float vAlpha;
      
      void main() {
        float d = length(gl_PointCoord - vec2(0.5));
        if (d > 0.5) discard;
        
        float glow = exp(-d * d * 4.0);
        vec3 color = vec3(0.25, 0.7, 1.0);
        
        gl_FragColor = vec4(color, glow * vAlpha);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  return new THREE.Points(geometry, material)
}

// ========== 初始化场景 ==========
function init() {
  if (!containerRef.value) return

  // 场景
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x020510)
  scene.fog = new THREE.FogExp2(0x020510, 0.018)  // 更柔和的雾

  // 使用窗口尺寸（全屏背景）
  const containerWidth = window.innerWidth
  const containerHeight = window.innerHeight
  
  // 相机 - 左前方俯视30度角，增强立体层次
  camera = new THREE.PerspectiveCamera(
    45,  // 更窄的视场角，增加远近感
    containerWidth / containerHeight,
    0.1,
    100
  )
  // 斜侧方仰视，增加宏伟感和空间纵深
  const cameraDistance = 16
  const cameraHeight = 0.5  // 更低的视角，增强仰视感
  camera.position.set(-7, cameraHeight, cameraDistance)  // 更向左偏移
  camera.lookAt(3, 3, 0)  // 看向树的更高处

  // 渲染器 - 使用容器尺寸
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
  renderer.setSize(containerWidth, containerHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setClearColor(0x050a12, 1)
  containerRef.value.appendChild(renderer.domElement)

  // 后期处理 - Bloom（柔和光雾效果）
  composer = new EffectComposer(renderer)
  composer.addPass(new RenderPass(scene, camera))
  
  const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(containerWidth, containerHeight),
    1.3,   // strength
    0.9,   // radius - 大半径，柔和扩散
    0.12   // threshold - 低阈值，更多发光
  )
  composer.addPass(bloomPass)

  // 创建场景元素 - 缩小15%，在右侧
  treeParticles = createTreeParticles()
  treeParticles.scale.setScalar(0.6)  // 缩小15%
  treeParticles.position.set(4, 0, 0)
  scene.add(treeParticles)

  // 叶子发光粒子
  leafParticles = createLeafParticles()
  leafParticles.scale.setScalar(0.6)
  leafParticles.position.set(4, 0, 0)
  scene.add(leafParticles)

  // 地面波动粒子（保持原有的波浪效果）
  groundWaveParticles = createGroundWaveParticles()
  groundWaveParticles.position.set(4, -1.5, 0)  // 与树干底部对齐
  scene.add(groundWaveParticles)
  
  // 能量汇聚粒子（向心流动 + 攀爬树干）
  groundParticles = createParticleSea()
  groundParticles.position.set(4, -1.5, 0)  // 与树干底部对齐（-2.5 * 0.6 = -1.5）
  scene.add(groundParticles)

  // 根部能量光晕
  rootGlow = createRootGlow()
  rootGlow.scale.setScalar(0.6)
  rootGlow.position.set(4, -1.5, 0)  // 与树干底部对齐
  scene.add(rootGlow)

  dustParticles = createDustParticles()
  scene.add(dustParticles)

  // 横向连接粒子线（左右视觉桥梁）
  bridgeLines = createBridgeLines()
  scene.add(bridgeLines)

  // 事件监听
  window.addEventListener('resize', onResize)

  // 开始动画
  animate()
}

// ========== 动画循环 ==========
function animate() {
  animationId = requestAnimationFrame(animate)
  time += 0.016

  // 更新 Shader uniforms
  if (treeParticles) {
    (treeParticles.material as THREE.ShaderMaterial).uniforms.uTime.value = time
  }
  if (leafParticles) {
    (leafParticles.material as THREE.ShaderMaterial).uniforms.uTime.value = time
  }
  if (rootGlow) {
    (rootGlow.material as THREE.ShaderMaterial).uniforms.uTime.value = time
  }
  if (groundParticles) {
    (groundParticles.material as THREE.ShaderMaterial).uniforms.uTime.value = time
  }
  if (groundWaveParticles) {
    (groundWaveParticles.material as THREE.ShaderMaterial).uniforms.uTime.value = time
  }
  if (dustParticles) {
    (dustParticles.material as THREE.ShaderMaterial).uniforms.uTime.value = time
  }
  if (bridgeLines) {
    (bridgeLines.material as THREE.ShaderMaterial).uniforms.uTime.value = time
  }

  composer.render()
}

// ========== 窗口调整 ==========
function onResize() {
  if (!camera || !renderer || !composer) return
  
  // 使用窗口尺寸
  const width = window.innerWidth
  const height = window.innerHeight

  camera.aspect = width / height
  camera.updateProjectionMatrix()

  renderer.setSize(width, height)
  composer.setSize(width, height)
}

// ========== 滚动淡出效果 ==========
function onScroll() {
  const scrollY = window.scrollY
  const windowHeight = window.innerHeight
  // 在首屏滚动 0-80% 的高度范围内完成淡出
  const fadeDistance = windowHeight * 0.8
  scrollProgress.value = Math.min(scrollY / fadeDistance, 1)
}

// ========== 生命周期 ==========
onMounted(() => {
  init()
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()  // 初始化滚动状态
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('scroll', onScroll)
  
  if (renderer?.domElement?.parentElement) {
    renderer.domElement.parentElement.removeChild(renderer.domElement)
  }
  renderer?.dispose()
})
</script>

<template>
  <div 
    ref="containerRef" 
    class="spirit-tree"
    :style="{
      opacity: 1 - scrollProgress * 0.9,
      transform: `translateY(${-scrollProgress * 120}px) scale(${1 + scrollProgress * 0.1})`,
      filter: `blur(${scrollProgress * 4}px)`
    }"
  ></div>
</template>

<style scoped>
.spirit-tree {
  position: absolute;
  inset: 0;
  z-index: 1;
  pointer-events: none;
  overflow: hidden;
  will-change: opacity, transform, filter;
  transition: opacity 0.1s ease-out, transform 0.1s ease-out, filter 0.1s ease-out;
}
</style>
