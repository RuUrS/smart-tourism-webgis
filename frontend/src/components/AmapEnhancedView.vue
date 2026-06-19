<template>
  <div class="amap-enhanced-page">
    <div class="amap-toolbar">
      <button @click="toggleTraffic">
        {{ trafficVisible ? '隐藏实时路况' : '显示实时路况' }}
      </button>

      <button @click="loadHeatmap">
        加载动态热力图
      </button>

      <button @click="clearHeatmap">
        清除热力图
      </button>

      <button @click="goBack">
        返回主系统
      </button>
    </div>

    <div class="amap-status">
        {{ amapStatus }}
    </div>

    <div id="amapContainer" class="amap-container"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

let amap = null
let trafficLayer = null
let heatmap = null

const trafficVisible = ref(false)
const amapStatus = ref('正在加载高德地图...')

function loadAmapScript() {
  return new Promise((resolve, reject) => {
    if (window.AMap) {
      resolve()
      return
    }

    const amapKey = import.meta.env.VITE_AMAP_JS_KEY
    const securityCode = import.meta.env.VITE_AMAP_SECURITY_CODE

    if (!amapKey) {
      reject(new Error('未配置 VITE_AMAP_JS_KEY'))
      return
    }

    if (securityCode) {
      window._AMapSecurityConfig = {
        securityJsCode: securityCode
      }
    }

    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${amapKey}&plugin=AMap.HeatMap,AMap.ToolBar,AMap.Scale`
    script.onload = () => resolve()
    script.onerror = () => reject(new Error('高德 JS API 脚本加载失败，请检查 Key、安全密钥或网络'))
    document.head.appendChild(script)
  })
}

async function initAmap() {
  try {
    await nextTick()
    await loadAmapScript()

    const container = document.getElementById('amapContainer')

    if (!container) {
      throw new Error('未找到 amapContainer 容器')
    }

    amap = new window.AMap.Map('amapContainer', {
      zoom: 11,
      center: [111.65, 33.72],
      viewMode: '2D',
      resizeEnable: true
    })

    amap.addControl(new window.AMap.ToolBar())
    amap.addControl(new window.AMap.Scale())

    trafficLayer = new window.AMap.TileLayer.Traffic({
      zIndex: 10,
      autoRefresh: true,
      interval: 180
    })

    amapStatus.value = '高德地图加载成功'
  } catch (error) {
    console.error('高德地图初始化失败：', error)
    amapStatus.value = `高德地图初始化失败：${error.message}`
  }
}

function toggleTraffic() {
  if (!amap || !trafficLayer) {
    amapStatus.value = '地图尚未初始化，无法显示实时路况'
    return
  }

  if (trafficVisible.value) {
    trafficLayer.setMap(null)
    trafficVisible.value = false
    amapStatus.value = '已隐藏实时路况'
  } else {
    trafficLayer.setMap(amap)
    trafficVisible.value = true
    amapStatus.value = '已显示高德实时路况'
  }
}

async function loadHeatmap() {
  if (!amap) {
    amapStatus.value = '地图尚未初始化，无法加载热力图'
    return
  }

  try {
    const response = await fetch('/api/crowd/heatmap')

    if (!response.ok) {
      throw new Error(`热力图接口请求失败：HTTP ${response.status}`)
    }

    const data = await response.json()

    const sourceList = data.items || data.features || []

    const heatData = sourceList.map(item => {
      if (item.geometry && item.geometry.coordinates) {
        return {
          lng: Number(item.geometry.coordinates[0]),
          lat: Number(item.geometry.coordinates[1]),
          count: Number(item.properties?.crowd_value || item.properties?.value || 50)
        }
      }

      return {
        lng: Number(item.lng),
        lat: Number(item.lat),
        count: Number(item.crowd_value || item.value || 50)
      }
    }).filter(item => item.lng && item.lat)

    if (!heatmap) {
      heatmap = new window.AMap.HeatMap(amap, {
        radius: 25,
        opacity: [0, 0.8]
      })
    }

    heatmap.setDataSet({
      data: heatData,
      max: 100
    })

    amapStatus.value = `动态热力图加载成功，共 ${heatData.length} 个点`
  } catch (error) {
    console.error('动态热力图加载失败：', error)
    amapStatus.value = `动态热力图加载失败：${error.message}`
  }
}

function clearHeatmap() {
  if (heatmap) {
    heatmap.setDataSet({
      data: [],
      max: 100
    })
  }

  amapStatus.value = '已清除热力图'
}

function goBack() {
  router.push('/')
}

onMounted(() => {
  initAmap()
})
</script>

<style scoped>
.amap-enhanced-page {
  width: 100vw;
  height: 100vh;
  position: relative;
  background: #f5f7fa;
}

.amap-container {
  width: 100%;
  height: 100%;
}

.amap-toolbar {
  position: absolute;
  z-index: 999;
  top: 16px;
  left: 16px;
  display: flex;
  gap: 8px;
  background: white;
  padding: 10px;
  border-radius: 8px;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.18);
}

.amap-toolbar button {
  padding: 8px 12px;
  background: #2f80ed;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.amap-status {
  position: absolute;
  z-index: 999;
  top: 78px;
  left: 16px;
  max-width: 520px;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 13px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.12);
}
</style>