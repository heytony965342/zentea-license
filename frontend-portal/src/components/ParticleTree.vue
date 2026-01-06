<script setup lang="ts">
/**
 * 粒子茶树交互系统
 * 使用 Three.js 实现的 3D 粒子树效果
 */
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'

// 可配置属性（后台可控）
interface Props {
  primaryColor?: string      // 主色（森林绿）
  accentColor?: string       // 点缀色（数字金）
  particleCount?: number     // 粒子数量
  rotationSpeed?: number     // 旋转速度
  interactionStrength?: number // 交互灵敏度
  growthSpeed?: number       // 生长速度
}

const props = withDefaults(defineProps<Props>(), {
  primaryColor: '#1a472a',
  accentColor: '#d4af37',
  particleCount: 8000,
  rotationSpeed: 0.15,
  interactionStrength: 0.5,
  growthSpeed: 1.0,
})

const containerRef = ref<HTMLDivElement>()
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let particles: THREE.Points
let animationId: number
let mouseX = 0
let mouseY = 0
let targetRotationX = 0
let targetRotationY = 0
let growthProgress = 0

// 使用柏林噪声模拟自然扭曲
function noise2D(x: number, y: number): number {
  // 简化的伪噪声函数
  const n = Math.sin(x * 12.9898 + y * 78.233) * 43758.5453
  return (n - Math.floor(n)) * 2 - 1
}

function fbm(x: number, y: number, octaves: number = 4): number {
  let value = 0
  let amplitude = 0.5
  let frequency = 1
  for (let i = 0; i < octaves; i++) {
    value += amplitude * noise2D(x * frequency, y * frequency)
    amplitude *= 0.5
    frequency *= 2
  }
  return value
}

// 生成老树主干的扭曲路径
function getTrunkOffset(y: number, angle: number): { x: number, z: number } {
  // 多层次的自然弯曲 - 加大参数让效果更明显
  const bendStrength = 0.8
  
  // 主弯曲 - 整体的大弧度弯曲（像老树被风吹歪）
  // 使用多个正弦波叠加，模拟老树蜿蜒的形态
  const mainBendX = Math.sin(y * 1.2 + 0.5) * bendStrength * 0.5 
                  + Math.sin(y * 0.5 + 2.0) * bendStrength * 0.3
  const mainBendZ = Math.cos(y * 0.8 + 1.5) * bendStrength * 0.4
                  + Math.cos(y * 1.5 + 0.3) * bendStrength * 0.2
  
  // 次级扭曲 - 中等频率的蜿蜒（树干的弯折）
  const twistX = fbm(y * 3.0, 0.5, 3) * 0.25
  const twistZ = fbm(0.5, y * 3.0, 3) * 0.25
  
  // 细节纹理 - 高频的树皮凹凸感
  const barkX = noise2D(y * 8, angle * 3) * 0.08
  const barkZ = noise2D(angle * 3, y * 8) * 0.08
  
  return {
    x: mainBendX + twistX + barkX,
    z: mainBendZ + twistZ + barkZ
  }
}

// 生成茶树形状的粒子位置
function generateTreePositions(count: number, growth: number): Float32Array {
  const positions = new Float32Array(count * 3)
  
  // 树干分叉点（老树特征）- 增强分叉效果
  const branchPoints = [
    { y: -1.1, angle: 0.4, strength: 0.35 },
    { y: -0.8, angle: 2.5, strength: 0.30 },
    { y: -0.5, angle: 4.8, strength: 0.40 },
    { y: -0.6, angle: 1.2, strength: 0.25 },
  ]
  
  for (let i = 0; i < count; i++) {
    const i3 = i * 3
    
    // 树的高度分布（底部密集，顶部稀疏）
    const heightRatio = Math.pow(Math.random(), 0.7)
    const y = heightRatio * 4 * growth - 1.5  // -1.5 到 2.5
    
    // 圆形分布角度
    const angle = Math.random() * Math.PI * 2
    
    // 根据高度计算半径（树冠形状）
    let radius: number
    let offsetX = 0
    let offsetZ = 0
    
    if (y < -0.5) {
      // ========== 老树主干部分 ==========
      
      // 基础半径：底部粗，向上逐渐变细（老树的锥形）
      const trunkProgress = (y + 1.5) / 1.0  // 0 到 1
      const baseRadius = 0.35 - trunkProgress * 0.12  // 底部更粗
      
      // 添加不规则的粗细变化（树瘤、年轮凸起）
      const bulgeNoise = fbm(y * 4, angle, 3)
      const bulge = Math.max(0, bulgeNoise) * 0.15  // 增大树瘤效果
      
      // 树皮纹理 - 让边缘更不规则
      const barkRoughness = noise2D(angle * 6, y * 10) * 0.06
      
      radius = baseRadius + bulge + barkRoughness + Math.random() * 0.05
      
      // 获取主干扭曲偏移
      const trunkOffset = getTrunkOffset(y, angle)
      offsetX = trunkOffset.x
      offsetZ = trunkOffset.z
      
      // 添加树根部分的扩张（y 接近 -1.5 时）
      if (y < -1.2) {
        const rootFactor = (-1.2 - y) / 0.3  // 0 到 1
        const rootSpread = rootFactor * 0.5  // 增大根部扩张
        const rootAngle = angle + noise2D(angle, y) * 0.8
        offsetX += Math.cos(rootAngle) * rootSpread
        offsetZ += Math.sin(rootAngle) * rootSpread
        radius += rootFactor * 0.15
      }
      
      // 模拟老树的分叉暗示（一些粒子向外延伸）
      for (const branch of branchPoints) {
        const dist = Math.abs(y - branch.y)
        if (dist < 0.2 && Math.random() < 0.4) {
          const branchFactor = 1 - dist / 0.2
          const branchAngleDiff = Math.abs(angle - branch.angle)
          if (branchAngleDiff < 1.0 || branchAngleDiff > Math.PI * 2 - 1.0) {
            offsetX += Math.cos(branch.angle) * branch.strength * branchFactor * 1.5
            offsetZ += Math.sin(branch.angle) * branch.strength * branchFactor * 1.5
            radius += branch.strength * branchFactor * 0.8
          }
        }
      }
      
    } else {
      // ========== 树冠部分 ==========
      const crownY = (y + 0.5) / 3
      const maxRadius = 1.8 * (1 - crownY * 0.6)
      radius = maxRadius * Math.sqrt(Math.random())
      
      // 树冠也要继承主干的弯曲趋势（但逐渐减弱）
      const inheritFactor = Math.max(0, 1 - (y + 0.5) * 0.5)
      const trunkOffset = getTrunkOffset(-0.5, angle)
      offsetX = trunkOffset.x * inheritFactor
      offsetZ = trunkOffset.z * inheritFactor
    }
    
    // 最终位置
    positions[i3] = Math.cos(angle) * radius + offsetX
    positions[i3 + 1] = y
    positions[i3 + 2] = Math.sin(angle) * radius + offsetZ
    
    // 添加一些随机偏移使其更自然
    positions[i3] += (Math.random() - 0.5) * 0.15
    positions[i3 + 2] += (Math.random() - 0.5) * 0.15
  }
  
  return positions
}

// 生成粒子颜色
function generateColors(count: number, primary: string, accent: string): Float32Array {
  const colors = new Float32Array(count * 3)
  const primaryRGB = hexToRgb(primary)
  const accentRGB = hexToRgb(accent)
  
  for (let i = 0; i < count; i++) {
    const i3 = i * 3
    const useAccent = Math.random() < 0.15  // 15% 使用点缀色
    
    if (useAccent) {
      colors[i3] = accentRGB.r / 255
      colors[i3 + 1] = accentRGB.g / 255
      colors[i3 + 2] = accentRGB.b / 255
    } else {
      // 主色带一些变化
      const variation = 0.8 + Math.random() * 0.4
      colors[i3] = (primaryRGB.r / 255) * variation
      colors[i3 + 1] = (primaryRGB.g / 255) * variation
      colors[i3 + 2] = (primaryRGB.b / 255) * variation
    }
  }
  
  return colors
}

function hexToRgb(hex: string) {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
  return result ? {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16)
  } : { r: 26, g: 71, b: 42 }
}

function init() {
  if (!containerRef.value) return
  
  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight
  
  // 场景
  scene = new THREE.Scene()
  
  // 相机
  camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 100)
  camera.position.z = 5
  camera.position.y = 0.5
  
  // 渲染器
  renderer = new THREE.WebGLRenderer({ 
    antialias: true, 
    alpha: true,
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.setClearColor(0x000000, 0)
  containerRef.value.appendChild(renderer.domElement)
  
  // 创建粒子
  createParticles()
  
  // 添加环境光晕
  addGlow()
  
  // 事件监听
  window.addEventListener('resize', onResize)
  window.addEventListener('mousemove', onMouseMove)
  
  // 开始动画
  animate()
}

function createParticles() {
  const geometry = new THREE.BufferGeometry()
  
  // 初始位置（未生长状态）
  const positions = generateTreePositions(props.particleCount, 0)
  const colors = generateColors(props.particleCount, props.primaryColor, props.accentColor)
  
  // 存储目标位置（完全生长状态）
  const targetPositions = generateTreePositions(props.particleCount, 1)
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))
  geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  geometry.setAttribute('targetPosition', new THREE.BufferAttribute(targetPositions, 3))
  
  // 粒子大小随机
  const sizes = new Float32Array(props.particleCount)
  for (let i = 0; i < props.particleCount; i++) {
    sizes[i] = 2 + Math.random() * 3
  }
  geometry.setAttribute('size', new THREE.BufferAttribute(sizes, 1))
  
  // 自定义着色器材质
  const material = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      pixelRatio: { value: renderer.getPixelRatio() },
    },
    vertexShader: `
      attribute float size;
      attribute vec3 color;
      varying vec3 vColor;
      uniform float time;
      uniform float pixelRatio;
      
      void main() {
        vColor = color;
        
        // 添加微小的浮动动画
        vec3 pos = position;
        pos.y += sin(time * 2.0 + position.x * 3.0) * 0.02;
        pos.x += cos(time * 1.5 + position.z * 2.0) * 0.02;
        
        vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
        gl_PointSize = size * pixelRatio * (300.0 / -mvPosition.z);
        gl_Position = projectionMatrix * mvPosition;
      }
    `,
    fragmentShader: `
      varying vec3 vColor;
      
      void main() {
        // 圆形粒子
        float dist = length(gl_PointCoord - vec2(0.5));
        if (dist > 0.5) discard;
        
        // 边缘柔和
        float alpha = 1.0 - smoothstep(0.3, 0.5, dist);
        
        // 发光效果
        vec3 glow = vColor * (1.0 + (1.0 - dist * 2.0) * 0.5);
        
        gl_FragColor = vec4(glow, alpha * 0.8);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  })
  
  particles = new THREE.Points(geometry, material)
  scene.add(particles)
}

function addGlow() {
  // 底部光晕
  const glowGeometry = new THREE.PlaneGeometry(6, 2)
  const glowMaterial = new THREE.ShaderMaterial({
    uniforms: {
      color: { value: new THREE.Color(props.primaryColor) },
      time: { value: 0 },
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 color;
      uniform float time;
      varying vec2 vUv;
      
      void main() {
        float dist = length(vUv - vec2(0.5));
        float alpha = smoothstep(0.5, 0.0, dist) * 0.3;
        alpha *= 0.8 + sin(time) * 0.2;
        gl_FragColor = vec4(color, alpha);
      }
    `,
    transparent: true,
    side: THREE.DoubleSide,
  })
  
  const glow = new THREE.Mesh(glowGeometry, glowMaterial)
  glow.position.y = -1.8
  glow.rotation.x = -Math.PI / 2
  scene.add(glow)
}

function animate() {
  animationId = requestAnimationFrame(animate)
  
  const time = performance.now() * 0.001
  
  // 更新着色器时间
  if (particles) {
    const material = particles.material as THREE.ShaderMaterial
    material.uniforms.time.value = time
    
    // 生长动画
    if (growthProgress < 1) {
      growthProgress += 0.005 * props.growthSpeed
      growthProgress = Math.min(1, growthProgress)
      
      const positions = particles.geometry.getAttribute('position') as THREE.BufferAttribute
      const targets = particles.geometry.getAttribute('targetPosition') as THREE.BufferAttribute
      
      for (let i = 0; i < props.particleCount; i++) {
        const i3 = i * 3
        // 从底部开始生长
        const delay = targets.array[i3 + 1] / 4 + 0.5  // 基于高度的延迟
        const progress = Math.max(0, Math.min(1, (growthProgress - delay * 0.3) / 0.7))
        const eased = easeOutCubic(progress)
        
        positions.array[i3] = targets.array[i3] * eased
        positions.array[i3 + 1] = targets.array[i3 + 1] * eased - 1.5 * (1 - eased)
        positions.array[i3 + 2] = targets.array[i3 + 2] * eased
      }
      positions.needsUpdate = true
    }
    
    // 鼠标交互旋转
    targetRotationY += (mouseX * 0.5 - targetRotationY) * 0.05
    targetRotationX += (mouseY * 0.3 - targetRotationX) * 0.05
    
    particles.rotation.y = targetRotationY + time * props.rotationSpeed * 0.1
    particles.rotation.x = targetRotationX * 0.3
  }
  
  renderer.render(scene, camera)
}

function easeOutCubic(x: number): number {
  return 1 - Math.pow(1 - x, 3)
}

function onResize() {
  if (!containerRef.value) return
  
  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

function onMouseMove(e: MouseEvent) {
  mouseX = (e.clientX / window.innerWidth - 0.5) * 2 * props.interactionStrength
  mouseY = (e.clientY / window.innerHeight - 0.5) * 2 * props.interactionStrength
}

function cleanup() {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', onResize)
  window.removeEventListener('mousemove', onMouseMove)
  
  if (renderer && containerRef.value) {
    containerRef.value.removeChild(renderer.domElement)
    renderer.dispose()
  }
  
  if (particles) {
    particles.geometry.dispose()
    ;(particles.material as THREE.Material).dispose()
  }
}

onMounted(() => {
  setTimeout(init, 100)  // 确保 DOM 已渲染
})

onUnmounted(cleanup)

// 响应配置变化
watch(() => [props.primaryColor, props.accentColor], () => {
  if (particles) {
    const colors = generateColors(props.particleCount, props.primaryColor, props.accentColor)
    particles.geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3))
  }
})
</script>

<template>
  <div ref="containerRef" class="particle-tree"></div>
</template>

<style scoped>
.particle-tree {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
</style>

