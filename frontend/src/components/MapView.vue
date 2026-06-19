<template>
  <div class="map-page" :class="{ 'mobile-sidebar-open': mobileSidebarOpen }">
    <div v-if="mobileSidebarOpen" class="mobile-sidebar-mask" @click="closeMobileSidebar"></div>

    <div class="sidebar">
      <div class="mobile-sidebar-header">
        <span>功能菜单</span>
        <button type="button" @click="closeMobileSidebar">×</button>
      </div>
  <h2>老君山智能旅游 WebGIS</h2>
  <p>研究区：河南省洛阳市栾川县老君山</p>

  <details class="panel-box" open>
    <summary>地图控制</summary>

    <div class="button-row">
      <button @click="loadBoundary">加载边界</button>
      <button @click="loadPois()">加载 POI</button>
    </div>

    <div class="button-row">
      <button @click="triggerLocalGeojsonInput">
        加载本地边界
      </button>
      <button @click="clearLocalBoundary">
        清除本地边界
      </button>
    </div>
    <div class="button-row">
      <button @click="clearMapClickQuery">
        清除点击查询
      </button>
      <button @click="resetMapViewToLuanchuan">
        返回研究区
      </button>
    </div>
    <div class="button-row">
      <button @click="loadRoadNetwork()">加载路网</button>
      <button @click="clearRoadNetwork">清除路网</button>
    </div>
    <div class="button-row">
      <button @click="loadRoadNetwork('main_road')">主路</button>
      <button @click="loadRoadNetwork('scenic_road')">景区道路</button>
      <button @click="loadRoadNetwork('trail')">步道</button>
    </div>
    <div class="button-row">
      <button @click="openDashboard">
        数据大屏
      </button>
    </div>

    <input
      ref="localGeojsonInput"
      type="file"
      accept=".geojson,.json"
      style="display: none"
      @change="handleLocalGeojsonFile"
    />

    <div v-if="localBoundaryName" class="local-file-name">
      当前本地文件：{{ localBoundaryName }}
    </div>

    <div class="control-group">
      <div class="control-title">底图切换</div>
      <div class="button-row">
        <button
          :class="{ active: currentBaseMap === 'normal' }"
          @click="switchBaseMap('normal')"
        >
          普通地图
        </button>
        <button
          :class="{ active: currentBaseMap === 'satellite' }"
          @click="switchBaseMap('satellite')"
        >
          遥感影像
        </button>
      </div>
      <div class="button-row">
        <button
          :class="{ active: currentBaseMap === 'satelliteRoad' }"
          @click="switchBaseMap('satelliteRoad')"
        >
          影像路网
        </button>
        <button @click="openAmapEnhanced">
          高德增强模式
        </button>
      </div>
    </div>
  

    <div class="control-group">
      <div class="control-title">图层显示</div>

      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.boundary"
          @change="toggleLayer('boundary')"
        />
        栾川县边界
      </label>

      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.poi"
          @change="toggleLayer('poi')"
        />
        老君山 POI
      </label>

      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.nearby"
          @change="toggleLayer('nearby')"
        />
        附近查询结果
      </label>

      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.route"
          @change="toggleLayer('route')"
        />
        推荐路线
      </label>

      <label>
        <input
          type="checkbox"
          v-model="layerVisible.road"
          @change="toggleLayer('road')"
        />
        基础路网
      </label>

      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.onlineDistrict"
          @change="toggleLayer('onlineDistrict')"
        />
        在线行政区范围
      </label>
      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.onlineDistrictPoi"
          @change="toggleOnlineDistrictPoiLayer"
        />
        行政区搜索显示 POI 点
      </label>
      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.crowd"
          @change="toggleLayer('crowd')"
        />
        模拟客流点
      </label>
      <label class="layer-check">
        <input
          type="checkbox"
          v-model="layerVisible.crowdHeat"
          @change="toggleLayer('crowdHeat')"
        />
        客流热力图
      </label>
    </div>
  </details>

  <details class="panel-box" open>
    <summary>POI 名称搜索</summary>

    <input
      v-model="searchKeyword"
      class="search-input"
      placeholder="请输入景点、索道或服务名称"
      @keyup.enter="loadPois(currentType)"
    />

    <div class="button-row">
      <button @click="loadPois(currentType)">搜索</button>
      <button @click="resetPois">重置</button>
    </div>
  </details>

  <!-- 这里新增 POI 类型筛选按钮 -->
  <details class="panel-box">
    <summary>POI 类型筛选</summary>
    <button @click="loadPois()">全部 POI</button>
    <button @click="loadPois('attraction')">景点</button>
    <button @click="loadPois('transport')">交通/索道</button>
    <button @click="loadPois('service')">服务设施</button>
  </details>

  <div class="info-box">
    <p><b>当前状态：</b></p>
    <p>{{ statusText }}</p>
  </div>
  
  <details class="panel-box detail-panel" open>
    <summary>景点详情</summary>

    <div class="detail-box">
      <div v-if="selectedPoi" class="detail-content">
        <div class="detail-title">
          {{ selectedPoi.name }}
        </div>

        <div class="detail-row">
          <span class="detail-label">类型：</span>
          <span>{{ getTypeName(selectedPoi.type) }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">子类型：</span>
          <span>{{ getSubTypeName(selectedPoi.subtype) }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">地址：</span>
          <span>{{ selectedPoi.address || '暂无地址信息' }}</span>
        </div>

        <div class="detail-desc">
          <span class="detail-label">简介：</span>
          <p>{{ selectedPoi.description || '暂无简介' }}</p>
        </div>

        <div class="detail-row">
          <span class="detail-label">经纬度：</span>
          <span>{{ selectedPoi.lng }}, {{ selectedPoi.lat }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">来源：</span>
          <span>{{ selectedPoi.source || '未注明' }}</span>
        </div>

        <div class="detail-row">
          <span class="detail-label">核验：</span>
          <span>{{ selectedPoi.verify_status || '未核验' }}</span>
        </div>

        <div class="button-row">
          <button @click="flyToPoi(selectedPoi)">定位到该点</button>
          <button @click="queryNearbyServices">附近服务</button>
        </div>

        <div class="button-row">
          <button @click="setRouteStart(selectedPoi)">设为起点</button>
          <button @click="setRouteEnd(selectedPoi)">设为终点</button>
        </div>

        <button class="reset-btn" @click="resetSelectedPoi">
          重置景点详情
        </button>
      </div>

      <div v-else class="detail-empty">
        请点击地图上的 POI，或点击左侧 POI 列表查看详情。
      </div>
    </div>
  </details>

  <details class="panel-box">
    <summary>附近服务查询</summary>

    <p v-if="selectedPoi">
      当前选中：<b>{{ selectedPoi.name }}</b>
    </p>

    <p v-else>
      请先点击地图上的 POI 或左侧列表中的 POI
    </p>

    <select v-model="nearbyRadius" class="select-input">
      <option :value="500">500 米</option>
      <option :value="1000">1000 米</option>
      <option :value="2000">2000 米</option>
    </select>

    <div class="button-row">
      <button @click="queryNearbyServices">查询附近服务</button>
      <button @click="clearNearby">清除</button>
    </div>

    <div v-if="nearbyList.length > 0" class="nearby-list">
      <div
        v-for="item in nearbyList"
        :key="item.id"
        class="nearby-item"
        @click="flyToPoi(item)"
      >
        <b>{{ item.name }}</b>
        <span>{{ item.type }} / {{ item.subtype }}</span>
        <span>距离：{{ item.distance_m }} 米</span>
      </div>
    </div>
  </details>
  <details class="panel-box">
    <summary>高德路径规划</summary>

    <div class="route-plan-box">
      <div class="route-plan-row">
        <span class="route-plan-label">起点：</span>
        <span>{{ routeStart ? routeStart.name : '未设置' }}</span>
      </div>

      <div class="route-plan-row">
        <span class="route-plan-label">终点：</span>
        <span>{{ routeEnd ? routeEnd.name : '未设置' }}</span>
      </div>

      <select v-model="amapRouteMode" class="select-input">
        <option value="" disabled>请选择路线方式</option>
        <option value="walking">步行路线</option>
        <option value="driving">驾车路线</option>
      </select>

      <div class="button-row">
        <button @click="planAmapRoute">开始规划</button>
        <button @click="clearAmapRoute">清除路线</button>
      </div>

      <div v-if="amapRouteSummary" class="route-summary">
        <p>距离：{{ amapRouteSummary.distanceText }}</p>
        <p>预计时间：{{ amapRouteSummary.durationText }}</p>
        <p>方式：{{ amapRouteSummary.modeText }}</p>
      </div>
    </div>
  </details>
  <details class="panel-box">
    <summary>周边交通态势</summary>

    <div class="traffic-box">
      <div class="traffic-row">
        <span class="traffic-label">查询对象：</span>
        <select v-model="trafficTargetType" class="select-input">
          <option value="ticket">票务中心</option>
          <option value="selectedPoi">当前选中 POI</option>
          <option value="mapClick">地图点击位置</option>
        </select>
      </div>
      <div class="traffic-row">
        <span class="traffic-label">查询半径：</span>
        <select v-model="trafficRadius" class="select-input">
          <option :value="1000">1000 米</option>
          <option :value="3000">3000 米</option>
          <option :value="5000">5000 米</option>
        </select>
      </div>
      <div class="button-row">
        <button @click="queryTrafficStatus">
          查询交通
        </button>
        <button @click="clearTrafficStatus">
          清除交通
        </button>
      </div>
      <div v-if="trafficInfo" class="traffic-summary">
        <p>查询对象：{{ trafficInfo.targetName }}</p>
        <p>查询方式：{{ getTrafficQueryModeName(trafficInfo.query_mode) }}</p>
        <p v-if="trafficInfo.matched_road || trafficInfo.road_name">
          匹配道路：{{ trafficInfo.matched_road || trafficInfo.road_name }}
        </p>
        <p>选择半径：{{ trafficInfo.radius }} 米</p>
        <p v-if="trafficInfo.used_radius">
          实际半径：{{ trafficInfo.used_radius }} 米
        </p>
        <p>交通评价：{{ trafficInfo.evaluation_description }}</p>
        <p>畅通比例：{{ trafficInfo.expedite }}</p>
        <p>拥堵比例：{{ trafficInfo.congested }}</p>
        <p>阻塞比例：{{ trafficInfo.blocked }}</p>
        <p>描述：{{ trafficInfo.description }}</p>
        <p>高德返回：{{ trafficInfo.amap_info || '暂无' }}</p>
        <p>高德状态码：{{ trafficInfo.amap_infocode || '暂无' }}</p>
      </div>
    </div>
  </details>
  <details class="panel-box">
    <summary>模拟客流分析</summary>

    <div class="crowd-box">
      <div class="crowd-row">
        <span class="crowd-label">模拟时间段：</span>
        <select v-model="crowdTimeSlot" class="select-input">
          <option value="上午">上午</option>
          <option value="中午">中午</option>
          <option value="下午">下午</option>
          <option value="傍晚">傍晚</option>
        </select>
      </div>
      <div class="button-row">
        <button @click="simulateCrowd">
          生成客流
        </button>
        <button @click="loadCrowdStatus">
          加载客流
        </button>
      </div>
      <div class="button-row">
        <button @click="loadCrowdHeatmap">
          加载热力图
        </button>
        <button @click="clearCrowdLayers">
          清除客流
        </button>
      </div>
      <div v-if="crowdSummary" class="crowd-summary">
        <p>客流点数量：{{ crowdSummary.total }}</p>
        <p>拥挤点：{{ crowdSummary.crowdedCount }} 个</p>
        <p>适中点：{{ crowdSummary.mediumCount }} 个</p>
        <p>舒适点：{{ crowdSummary.comfortableCount }} 个</p>

        <p v-if="crowdSummary.mostCrowded.length">
          主要拥挤点：
          {{ crowdSummary.mostCrowded.join('、') }}
        </p>
      </div>
      <div class="crowd-legend">
        <span><i class="legend-dot comfortable"></i>舒适</span>
        <span><i class="legend-dot medium"></i>适中</span>
        <span><i class="legend-dot crowded"></i>拥挤</span>
      </div>
    </div>
  </details>
  <details class="panel-box">
    <summary>动态路线推荐</summary>

    <div class="dynamic-box">
      <div class="dynamic-row">
        <span class="dynamic-label">游客类型：</span>
        <select v-model="dynamicUserType" class="select-input">
          <option value="first_time">初次游玩</option>
          <option value="normal">体力一般</option>
          <option value="strong">体力较好</option>
        </select>
      </div>

      <button @click="loadDynamicRouteRecommend">
        生成动态推荐
      </button>

      <div v-if="dynamicBestRoute" class="dynamic-result">
        <h4>推荐结果</h4>

        <p>
          推荐路线：
          {{ dynamicBestRoute.route.route_name }}
        </p>

        <p>
          推荐得分：
          {{ dynamicBestRoute.score }}
        </p>

        <p>
          预计时间：
          {{ dynamicBestRoute.route.estimated_time }}
        </p>

        <p>
          适合人群：
          {{ dynamicBestRoute.route.suitable_user }}
        </p>

        <p>
          路线节点：
          {{ dynamicBestRoute.route.node_sequence }}
        </p>

        <div v-if="dynamicBestRoute.reasons.length">
          <b>推荐理由：</b>
          <ul>
            <li
              v-for="item in dynamicBestRoute.reasons"
              :key="item"
            >
              {{ item }}
            </li>
          </ul>
        </div>

        <div v-if="dynamicBestRoute.warnings.length">
          <b>风险提示：</b>
          <ul>
            <li
              v-for="item in dynamicBestRoute.warnings"
              :key="item"
            >
              {{ item }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </details>    
  <details class="panel-box">
    <summary>游览路线推荐</summary>

    <div
      v-for="route in routeList"
      :key="route.id"
      class="route-item"
      :style="{ borderLeft: '6px solid ' + getRouteColor(route.difficulty) }"
      @click="showRoute(route.id)"
    >
      <b>{{ route.route_name }}</b>
      <span>难度：{{ route.difficulty }}</span>
      <span>预计时间：{{ route.estimated_time }}</span>
    </div>

    <div v-if="selectedRoute" class="route-detail">
      <h4>{{ selectedRoute.route_name }}</h4>
      <p>难度：{{ selectedRoute.difficulty }}</p>
      <p>预计时间：{{ selectedRoute.estimated_time }}</p>
      <p>适合人群：{{ selectedRoute.suitable_user }}</p>
      <p>{{ selectedRoute.description }}</p>

      <button @click="clearRoute">清除路线</button>
    </div>
  </details>

      <details class="panel-box poi-panel">
        <summary>POI 列表（{{ poiList.length }} 个）</summary>

        <div class="poi-list">
          <div
            v-for="poi in poiList"
            :key="poi.id"
            class="poi-item"
            @click="flyToPoi(poi)"
          >
            <b>{{ poi.name }}</b>
            <span>{{ getTypeName(poi.type) }} / {{ getSubTypeName(poi.subtype) }}</span>
          </div>
        </div>
      </details>
    </div>

    <div class="map-wrapper">
      <button type="button" class="mobile-menu-btn" @click="openMobileSidebar">☰ 功能</button>
      <div id="map"></div> /**地图区域 */
      /**顶部搜索框 */
      <div class="top-search-box">
        <button
          class="location-btn"
          title="定位我的当前位置"
          @click="locateUser"
        >
          📍
        </button>

        <input
          v-model="onlineSearchKeyword"
          placeholder="搜索在线地图地点，例如：老君山停车场"
          @keyup.enter="searchOnlinePoi"
        />

        <button class="search-btn" @click="searchOnlinePoi">
          搜索
        </button>

        <button class="clear-search-btn" @click="clearOnlineSearchResults">
          清除
        </button>
      </div>
      <!-- 右上角天气信息 -->
      <div
        :class="[
          'weather-card',
          weatherPanelOpen ? 'weather-expanded' : 'weather-mini',
          getWeatherClass(weatherInfo.weather)
        ]"
      >
        <!-- 展开状态：详细天气卡片 -->
        <template v-if="weatherPanelOpen">
          <div class="weather-header">
            <div class="weather-title">{{ weatherInfo.city || '栾川县' }}天气</div>
            <button class="weather-collapse-btn" @click="weatherPanelOpen = false">
              收起
            </button>
          </div>

          <div class="weather-main">
            <span class="weather-icon">{{ getWeatherIcon(weatherInfo.weather) }}</span>
            <span>{{ weatherInfo.weather }} / {{ weatherInfo.temperature }}℃</span>
          </div>

          <div class="weather-row">
            风力：{{ weatherInfo.wind }}
          </div>

          <div class="weather-row">
            湿度：{{ weatherInfo.humidity }}%
          </div>

          <div class="weather-row">
            数据发布时间：{{ weatherInfo.reporttime || '暂无' }}
          </div>

          <div class="weather-row">
            本地刷新时间：{{ weatherInfo.fetched_at || '暂无' }}
          </div>
          
          <div class="weather-follow-box">
            <label class="weather-switch">
              <input
                type="checkbox"
                v-model="weatherFollowSearch"
                :disabled="!weatherTargetPoi"
                @change="toggleWeatherFollow"
              />
              <span>跟随选中点天气</span>
            </label>

            <div class="weather-target-text">
              当前匹配点：
              <span v-if="weatherTargetPoi">
                {{ weatherTargetPoi.name }}
                <template v-if="weatherTargetPoi.adname">
                  （{{ weatherTargetPoi.adname }}）
                </template>
              </span>
              <span v-else>
                暂无，请先点击在线搜索结果
              </span>
            </div>
          </div>
          <div class="weather-advice">
            {{ getWeatherAdviceText() }}
          </div>

            <button
              class="weather-refresh"
              @click="weatherFollowSearch && weatherTargetPoi?.adcode
                ? loadWeather('manual', weatherTargetPoi.adcode)
                : loadWeather('manual', defaultWeatherCity)"
            >
              刷新天气
            </button>
        </template>

        <!-- 折叠状态：小天气卡片 -->
        <template v-else>
          <div class="weather-mini-content" @click="weatherPanelOpen = true">
            <div class="weather-mini-temp">
              {{ weatherInfo.temperature }}℃
            </div>

            <div class="weather-mini-info">
              <div>{{ weatherInfo.city || '栾川县' }}</div>
              <div>{{ weatherInfo.weather }}</div>
            </div>

            <div class="weather-mini-icon">
              {{ getWeatherIcon(weatherInfo.weather) }}
            </div>

            <div class="weather-mini-label">
              天气
            </div>
          </div>
        </template>
      </div>

      <!-- 右下角 AI 旅游小助手按钮 -->
      <button
        class="assistant-fab"
        :style="{
          left: assistantFabPosition.x + 'px',
          top: assistantFabPosition.y + 'px'
        }"
        @mousedown.prevent="startAssistantFabDrag"
        @touchstart.prevent="startAssistantFabDrag"
        @touchend.stop.prevent="handleAssistantFabTouchEnd"
        @click.stop="handleAssistantFabClick"
      >
        🤖
      </button>

      <!-- AI 旅游小助手聊天窗口 -->
    <div
      v-if="assistantOpen"
      class="assistant-modal-mask"
    >
      <div class="assistant-panel assistant-panel-large">
          <div class="assistant-header">
            <strong>老君山旅游小助手</strong>
            <button class="assistant-close-btn" @click="closeAssistantPanel">×</button>
          </div>

        <div class="agent-tabs">
          <button
            v-for="item in agentTypes"
            :key="item.value"
            :class="{ active: activeAgentType === item.value }"
            @click="activeAgentType = item.value"
          >
            {{ item.label }}
          </button>
        </div>
        <div class="assistant-body">
          <div
            v-for="(msg, index) in assistantMessages"
            :key="index"
            :class="['assistant-message', msg.role]"
          >
            <div class="message-content">
              {{ msg.content }}
            </div>
            
            <div
              v-if="msg.role === 'assistant' && msg.meta"
              class="agent-execute-meta"
            >
              <div>
                <strong>Agent：</strong>
                {{ msg.meta.agent_name }}
              </div>
              <div>
                <strong>识别类型：</strong>
                {{ msg.meta.agent_type }}
              </div>
              <div v-if="msg.meta.used_tools && msg.meta.used_tools.length">
                <strong>调用工具：</strong>
                <span
                  v-for="(tool, toolIndex) in msg.meta.used_tools"
                  :key="toolIndex"
                  class="tool-tag"
                >
                  {{ tool.name }}
                </span>
              </div>
              
              <div v-if="msg.meta.map_action && msg.meta.map_action.type !== 'none'">
                <strong>地图动作：</strong>
                {{ msg.meta.map_action.type }}
              </div>
            </div>
          </div>
        </div>

        <div class="assistant-input-box">
          <textarea
            v-model="assistantQuestion"
            placeholder="例如：第一次去老君山怎么玩？"
            @keyup.enter.exact.prevent="sendAssistantQuestion"
          ></textarea>

          <button @click="sendAssistantQuestion">
            发送
          </button>
        </div>

        <div class="langchain-demo-box">
          <div class="langchain-demo-title">
            <span>LangChain Demo</span>
            <button @click="langchainDemoVisible = !langchainDemoVisible">
              {{ langchainDemoVisible ? '收起' : '测试' }}
            </button>
          </div>
          <div v-if="langchainDemoVisible" class="langchain-demo-content">
            <p class="langchain-demo-desc">
              主旅游小助手：正式功能；LangChain Demo：框架验证。
            </p>

            <textarea
              v-model="langchainDemoInput"
              class="langchain-demo-input"
              placeholder="输入测试问题，例如：今天老君山适合走哪条路线？"
            ></textarea>

            <button
              class="langchain-demo-btn"
              @click="runLangChainDemo"
              :disabled="langchainDemoLoading"
            >
              {{ langchainDemoLoading ? '测试中...' : 'LangChain Demo 测试' }}
            </button>
            <div v-if="langchainDemoResult" class="langchain-demo-result">
              {{ langchainDemoResult }}
            </div>
          </div>
        </div>

      </div>
    </div>
    </div>
    <div v-if="dashboardVisible" class="dashboard-overlay">
      <div class="dashboard-panel">
        <div class="dashboard-header">
          <h2>老君山智能旅游数据大屏</h2>
          <button @click="closeDashboard">关闭</button>
        </div>

        <div v-if="dashboardData" class="dashboard-cards">
          <div class="dashboard-card">
            <span class="card-title">POI 总数</span>
            <strong>{{ dashboardData.poi_total }}</strong>
          </div>

          <div class="dashboard-card">
            <span class="card-title">知识库条目</span>
            <strong>{{ dashboardData.knowledge_total }}</strong>
          </div>

          <div class="dashboard-card">
            <span class="card-title">客流点数量</span>
            <strong>
              {{
                dashboardData.crowd_by_level.reduce((sum, item) => sum + item.count, 0)
              }}
            </strong>
          </div>

          <div class="dashboard-card">
            <span class="card-title">路线类型数</span>
            <strong>{{ dashboardData.route_by_difficulty.length }}</strong>
          </div>

          <div class="dashboard-card">
            <span class="card-title">路网线段数</span>
            <strong>{{ dashboardData.road_total || 0 }}</strong>
          </div>

          <div class="dashboard-card">
            <span class="card-title">路网总长度</span>
            <strong>{{ dashboardData.road_length_km || 0 }} km</strong>
          </div>
        </div>

        <div class="dashboard-grid">
          <div id="poiTypeChart" class="dashboard-chart"></div>
          <div id="crowdLevelChart" class="dashboard-chart"></div>
          <div id="topCrowdChart" class="dashboard-chart"></div>
          <div id="routeChart" class="dashboard-chart"></div>
          <div id="roadTypeChart" class="dashboard-chart"></div>
          <div id="roadLengthChart" class="dashboard-chart"></div>
          <div id="roadWalkableChart" class="dashboard-chart"></div>
          <div id="roadVerifyChart" class="dashboard-chart"></div>
          <div id="agentTypeChart" class="dashboard-chart"></div>
          <div id="toolUsageChart" class="dashboard-chart"></div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { onMounted,onUnmounted, ref, reactive, nextTick } from 'vue'/**图层显示状态 */
import { saveUserRecord } from '../utils/auth'
import { useRouter } from 'vue-router'
const router = useRouter()
function openAmapEnhanced() {
  router.push('/amap-enhanced')
}
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'

let map = null
let boundaryLayer = null
let poiLayer = null
/**底图图层变量 */
let normalLayer = null
let satelliteLayer = null
let satelliteRoadLayer = null
const currentBaseMap = ref('normal')
const mobileSidebarOpen = ref(false)/**移动端 */
function refreshMapSize() {
  nextTick(() => {
    if (!map) return
    map.invalidateSize()
    setTimeout(() => map && map.invalidateSize(), 260)
  })
}
function openMobileSidebar() {
  mobileSidebarOpen.value = true
}
function closeMobileSidebar() {
  mobileSidebarOpen.value = false
  refreshMapSize()
}
function handleWindowResize() {
  if (window.innerWidth > 768) {
    mobileSidebarOpen.value = false
  }
  refreshMapSize()
}
/**默认点位 */
const caseCenter = [33.73, 111.65]
const caseZoom = 12
/**路网 */
let roadLayer = null
/**大屏变量 */
const dashboardVisible = ref(false)
const dashboardData = ref(null)

let poiTypeChart = null
let crowdLevelChart = null
let topCrowdChart = null
let routeChart = null
let roadTypeChart = null
let roadLengthChart = null
let roadWalkableChart = null
let roadVerifyChart = null/**核验状态统计 */
let agentTypeChart = null
let toolUsageChart = null
/**用户变量 */
let userLocationLayer = null
let userAccuracyCircle = null
const statusText = ref('地图初始化中...')
const poiList = ref([])
let mapClickLayer = null/**任意查询 */
const mapClickInfo = ref(null)
/**模拟客流变量 */
const crowdList = ref([])
const crowdTimeSlot = ref('上午')
const crowdSummary = ref(null)
let crowdLayer = null
let crowdHeatLayer = null
/**交通态势查询 */
const trafficTargetType = ref('ticket')
const trafficRadius = ref(3000)
const trafficInfo = ref(null)
let trafficCircleLayer = null
/**动态路线推荐 */
const dynamicUserType = ref('first_time')
const dynamicRecommendResult = ref(null)
const dynamicBestRoute = ref(null)
/**多Agent设计 */
const activeAgentType = ref('auto')
const agentTypes = [
  {
    value: 'auto',
    label: '自动规划'
  },
  {
    value: 'comprehensive',
    label: '综合建议'
  },
  {
    value: 'scenic',
    label: '景点讲解'
  },
  {
    value: 'route',
    label: '路线推荐'
  },
  {
    value: 'traffic',
    label: '交通出行'
  },
  {
    value: 'crowd',
    label: '客流分析'
  }
]
/**langchain */
const langchainDemoInput = ref('')
const langchainDemoLoading = ref(false)
const langchainDemoResult = ref('')
const langchainDemoVisible = ref(false)
/**天气跟随变量 */
const weatherFollowSearch = ref(false)
const weatherTargetPoi = ref(null)
const defaultWeatherCity = '410324'

const assistantOpen = ref(false)
const assistantQuestion = ref('')
const assistantFabPosition = ref({
  x: window.innerWidth - 96,
  y: window.innerHeight - 96
})

const assistantFabDragging = ref(false)
const assistantFabMoved = ref(false)

let assistantDragOffsetX = 0
let assistantDragOffsetY = 0
const assistantMessages = ref([
  {
    role: 'assistant',
    content: '你好，我是老君山旅游小助手。你可以问我路线推荐、景点介绍、附近服务或游览建议。'
  }
])

const weatherPanelOpen = ref(true)
const weatherInfo = ref({
  city: '栾川县',
  weather: '加载中',
  temperature: '--',
  wind: '--',
  humidity: '--',
  reporttime: '',
  fetched_at: '',
  advice: '正在获取实时天气信息...'
})

const layerVisible = reactive({
  boundary: false,
  poi: false,
  nearby: true,
  route: true,
  onlineDistrict: true,
  onlineDistrictPoi: false,
  crowd: false,
  crowdHeat: false,
  road: false
})
const routeList = ref([])
const selectedRoute = ref(null)

let routeLayer = null

const selectedPoi = ref(null)
const nearbyRadius = ref(1000)
const nearbyList = ref([])

let nearbyLayer = null
let nearbyCircle = null

const searchKeyword = ref('')
const currentType = ref('')
const onlineSearchKeyword = ref('')/**搜索框设计 */
const onlineSearchResults = ref([])

let onlineSearchLayer = null

const routeStart = ref(null)/**路径规划设计 */
const routeEnd = ref(null)
const amapRouteMode = ref('')
const amapRouteSummary = ref(null)
let amapRouteLayer = null
const localGeojsonInput = ref(null)
const localBoundaryName = ref('')
let localBoundaryLayer = null
/**行政区边界图层变量 */
let onlineDistrictLayer = null
const onlineDistrictName = ref('')
onMounted(() => {
  initMap()
  // 默认只定位到研究区，不自动加载边界和 POI
  if (map) {
    map.setView(caseCenter, caseZoom)
  }
  //loadBoundary()
  //loadPois()
  loadRoutes()//路线状态变量
  loadWeather('auto', defaultWeatherCity) //实时天气接入变量

  // 每 10 分钟自动刷新一次天气
  setInterval(() => {
    if (weatherFollowSearch.value && weatherTargetPoi.value?.adcode) {
      loadWeather('auto', weatherTargetPoi.value.adcode)
    } else {
      loadWeather('auto', defaultWeatherCity)
    }
  }, 10 * 60 * 1000)
  window.addEventListener('resize', handleWindowResize)
})
onUnmounted(() => {
  window.removeEventListener('resize', handleWindowResize)
})
//按钮拖动函数
function startAssistantFabDrag(event) {
  assistantFabDragging.value = true
  assistantFabMoved.value = false

  const point = event.touches ? event.touches[0] : event

  assistantDragOffsetX = point.clientX - assistantFabPosition.value.x
  assistantDragOffsetY = point.clientY - assistantFabPosition.value.y

  window.addEventListener('mousemove', moveAssistantFab)
  window.addEventListener('mouseup', stopAssistantFabDrag)
  window.addEventListener('touchmove', moveAssistantFab, { passive: false })
  window.addEventListener('touchend', stopAssistantFabDrag)
}
function moveAssistantFab(event) {
  if (!assistantFabDragging.value) return

  if (event.cancelable) {
    event.preventDefault()
  }

  const point = event.touches ? event.touches[0] : event

  let nextX = point.clientX - assistantDragOffsetX
  let nextY = point.clientY - assistantDragOffsetY

  const buttonSize = 64
  const margin = 8

  nextX = Math.max(margin, Math.min(window.innerWidth - buttonSize - margin, nextX))
  nextY = Math.max(margin, Math.min(window.innerHeight - buttonSize - margin, nextY))

  if (
    Math.abs(nextX - assistantFabPosition.value.x) > 3 ||
    Math.abs(nextY - assistantFabPosition.value.y) > 3
  ) {
    assistantFabMoved.value = true
  }

  assistantFabPosition.value = {
    x: nextX,
    y: nextY
  }
}
function stopAssistantFabDrag() {
  assistantFabDragging.value = false

  window.removeEventListener('mousemove', moveAssistantFab)
  window.removeEventListener('mouseup', stopAssistantFabDrag)
  window.removeEventListener('touchmove', moveAssistantFab)
  window.removeEventListener('touchend', stopAssistantFabDrag)
}
function openAssistantPanelFromFab() {
  if (assistantFabMoved.value) {
    assistantFabMoved.value = false
    return
  }

  assistantOpen.value = true
}
function handleAssistantFabTouchEnd() {
  // 手机上 touchstart.prevent 可能会阻止 click，
  // 所以手机端在 touchend 阶段主动打开小助手。
  stopAssistantFabDrag()
  openAssistantPanelFromFab()
}
function handleAssistantFabClick() {//点击按钮打开窗口函数
  openAssistantPanelFromFab()
}

function closeAssistantPanel() {//关闭小助手函数
  assistantOpen.value = false
}
//加载路网函数
async function loadRoadNetwork(roadType = '') {
  try {
    let url = '/api/roads'

    if (roadType) {
      url += `?road_type=${roadType}`
    }

    const response = await fetch(url)

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '路网接口请求失败')
    }

    const data = await response.json()

    if (roadLayer) {
      map.removeLayer(roadLayer)
      roadLayer = null
    }

    roadLayer = L.geoJSON(data, {
      style: feature => {
        const type = feature.properties.road_type
        const named = feature.properties.raw_name

        if (type === 'main_road') {
          return {
            color: '#34495e',
            weight: named ? 4 : 3,
            opacity: 0.85
          }
        }

        if (type === 'scenic_road') {
          return {
            color: '#2980b9',
            weight: named ? 3 : 2,
            opacity: 0.75
          }
        }

        if (type === 'trail') {
          return {
            color: '#27ae60',
            weight: 2,
            dashArray: '4,4',
            opacity: 0.8
          }
        }

        return {
          color: '#aaa',
          weight: 1.5,
          opacity: 0.4
        }
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties

        layer.bindPopup(`
          <b>${p.display_name || p.name || '道路'}</b><br>
          OSM原始名称：${p.raw_name || '无'}<br>
          OSM分类：${p.fclass || '暂无'}<br>
          系统分类：${getRoadTypeName(p.road_type)}<br>
          道路长度：${p.length_m ? p.length_m + ' 米' : '暂无'}<br>
          是否可步行：${p.walkable ? '是' : '否'}<br>
          最高限速：${p.maxspeed || '暂无'}<br>
          单行道：${p.oneway || '暂无'}<br>
          数据来源：${p.source || 'OpenStreetMap'}<br>
          数据状态：${p.verify_status || '待核验'}<br>
          <small>说明：该路网来自开放地图数据，主要用于基础展示和空间分析辅助。</small>
        `)
      }
    })

    roadLayer.addTo(map)
    layerVisible.road = true

    if (roadLayer.getBounds && roadLayer.getBounds().isValid()) {
      map.fitBounds(roadLayer.getBounds(), {
        padding: [40, 40]
      })
    }

    statusText.value = `路网数据加载成功，共 ${data.features.length} 条`
  } catch (error) {
    console.error(error)
    statusText.value = `路网数据加载失败：${error.message}`
  }
}
function getRoadTypeName(type) {
  if (type === 'main_road') return '主路'
  if (type === 'scenic_road') return '景区道路'
  if (type === 'trail') return '步道'
  return '其他道路'
}
function clearRoadNetwork() {//清除路网函数
  if (roadLayer) {
    map.removeLayer(roadLayer)
    roadLayer = null
  }
  layerVisible.road = false
  statusText.value = '已清除路网图层'
}
//大屏数据函数
async function openDashboard() {
  dashboardVisible.value = true

  await nextTick()
  await loadDashboardData()
}
function closeDashboard() {
  dashboardVisible.value = false
}
async function loadDashboardData() {
  try {
    const response = await fetch('/api/dashboard/summary')

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '数据大屏接口请求失败')
    }

    const data = await response.json()
    dashboardData.value = data
    await nextTick()
    renderDashboardCharts()
    statusText.value = '数据大屏加载成功'
  } catch (error) {
    console.error(error)
    statusText.value = `数据大屏加载失败：${error.message}`
  }
}
//渲染图表函数
function renderDashboardCharts() {
  if (!dashboardData.value) return

  renderPoiTypeChart()
  renderCrowdLevelChart()
  renderTopCrowdChart()
  renderRouteChart()
  renderRoadTypeChart()
  renderRoadLengthChart()
  renderRoadWalkableChart()
  renderRoadVerifyChart()
  renderAgentTypeChart()
  renderToolUsageChart()
}
function renderPoiTypeChart() {
  const el = document.getElementById('poiTypeChart')
  if (!el) return

  if (poiTypeChart) {
    poiTypeChart.dispose()
  }

  poiTypeChart = echarts.init(el)

  const data = dashboardData.value.poi_by_type || []

  poiTypeChart.setOption({
    title: {
      text: 'POI 类型统计',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: data.map(item => ({
          name: item.type || '未知',
          value: item.count
        }))
      }
    ]
  })
}
function renderCrowdLevelChart() {
  const el = document.getElementById('crowdLevelChart')
  if (!el) return

  if (crowdLevelChart) {
    crowdLevelChart.dispose()
  }

  crowdLevelChart = echarts.init(el)

  const data = dashboardData.value.crowd_by_level || []

  crowdLevelChart.setOption({
    title: {
      text: '客流等级统计',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: data.map(item => item.level || '未知')
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        type: 'bar',
        data: data.map(item => item.count)
      }
    ]
  })
}
function renderTopCrowdChart() {
  const el = document.getElementById('topCrowdChart')
  if (!el) return

  if (topCrowdChart) {
    topCrowdChart.dispose()
  }

  topCrowdChart = echarts.init(el)

  const data = dashboardData.value.top_crowd_pois || []

  topCrowdChart.setOption({
    title: {
      text: '热门客流 TOP5',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {},
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: data.map(item => item.name).reverse()
    },
    series: [
      {
        type: 'bar',
        data: data.map(item => item.crowd_value).reverse()
      }
    ]
  })
}
function renderRouteChart() {
  const el = document.getElementById('routeChart')
  if (!el) return

  if (routeChart) {
    routeChart.dispose()
  }

  routeChart = echarts.init(el)

  const data = dashboardData.value.route_by_difficulty || []

  routeChart.setOption({
    title: {
      text: '路线难度统计',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: data.map(item => ({
          name: item.difficulty || '未知',
          value: item.count
        }))
      }
    ]
  })
}
//道路类型数量统计
function renderRoadTypeChart() {
  const el = document.getElementById('roadTypeChart')
  if (!el) return

  if (roadTypeChart) {
    roadTypeChart.dispose()
  }

  roadTypeChart = echarts.init(el)

  const data = dashboardData.value.road_by_type || []

  roadTypeChart.setOption({
    title: {
      text: '基础路网类型统计',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item'
    },
    legend: {
      bottom: 0
    },
    series: [
      {
        type: 'pie',
        radius: ['35%', '60%'],
        data: data.map(item => ({
          name: getRoadTypeName(item.road_type),
          value: item.count
        }))
      }
    ]
  })
}
//各类道路长度统计
function renderRoadLengthChart() {
  const el = document.getElementById('roadLengthChart')
  if (!el) return

  if (roadLengthChart) {
    roadLengthChart.dispose()
  }

  roadLengthChart = echarts.init(el)

  const data = dashboardData.value.road_length_by_type || []

  roadLengthChart.setOption({
    title: {
      text: '各类道路长度统计',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}<br/>长度：{c} km'
    },
    xAxis: {
      type: 'category',
      data: data.map(item => getRoadTypeName(item.road_type))
    },
    yAxis: {
      type: 'value',
      name: 'km'
    },
    series: [
      {
        type: 'bar',
        data: data.map(item => item.length_km)
      }
    ]
  })
}
//可步行道路占比
function renderRoadWalkableChart() {
  const el = document.getElementById('roadWalkableChart')
  if (!el) return

  if (roadWalkableChart) {
    roadWalkableChart.dispose()
  }

  roadWalkableChart = echarts.init(el)

  const data = dashboardData.value.road_walkable || []

  roadWalkableChart.setOption({
    title: {
      text: '路网可步行性统计',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: '60%',
        data: data.map(item => ({
          name: item.walkable_status,
          value: item.count
        }))
      }
    ]
  })
}
//核验状态统计
function renderRoadVerifyChart() {
  const el = document.getElementById('roadVerifyChart')
  if (!el) return

  if (roadVerifyChart) {
    roadVerifyChart.dispose()
  }

  roadVerifyChart = echarts.init(el)

  const data = dashboardData.value.road_verify_status || []

  roadVerifyChart.setOption({
    title: {
      text: '路网数据核验状态',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: data.map(item => item.verify_status || '暂无')
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        type: 'bar',
        data: data.map(item => item.count)
      }
    ]
  })
}
function renderAgentTypeChart() {
  const el = document.getElementById('agentTypeChart')
  if (!el) return

  if (agentTypeChart) {
    agentTypeChart.dispose()
  }

  agentTypeChart = echarts.init(el)

  const data = dashboardData.value.agent_by_type || []

  agentTypeChart.setOption({
    title: {
      text: 'Agent 调用类型统计',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {
      trigger: 'item'
    },
    series: [
      {
        type: 'pie',
        radius: ['35%', '60%'],
        data: data.map(item => ({
          name: item.agent_name || '未知 Agent',
          value: item.count
        }))
      }
    ]
  })
}
function renderToolUsageChart() {
  const el = document.getElementById('toolUsageChart')
  if (!el) return

  if (toolUsageChart) {
    toolUsageChart.dispose()
  }

  toolUsageChart = echarts.init(el)

  const data = dashboardData.value.tool_usage_top || []

  toolUsageChart.setOption({
    title: {
      text: '工具调用次数 TOP5',
      left: 'center',
      textStyle: {
        fontSize: 14
      }
    },
    tooltip: {},
    xAxis: {
      type: 'value'
    },
    yAxis: {
      type: 'category',
      data: data.map(item => item.tool_name).reverse()
    },
    series: [
      {
        type: 'bar',
        data: data.map(item => item.count).reverse()
      }
    ]
  })
}
function getTrafficQueryModeName(mode) {
  if (mode === 'circle') return '圆形区域交通态势'
  if (mode === 'road_fallback') return '附近道路交通态势'
  return '暂无有效交通态势'
}
//动态路线推荐函数
async function loadDynamicRouteRecommend() {
  try {
    const response = await fetch(
      '/api/recommend/dynamic-route',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_type: dynamicUserType.value,
          time_slot: crowdTimeSlot.value,
          traffic_lng: 111.65632,
          traffic_lat: 33.774569,
          traffic_radius: 3000
        })
      }
    )
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '动态路线推荐失败')
    }

    const data = await response.json()

    dynamicRecommendResult.value = data
    dynamicBestRoute.value = data.best

    statusText.value = '动态路线推荐生成成功'
  } catch (error) {
    console.error(error)
    statusText.value = `动态路线推荐失败：${error.message}`
  }
}
//获取查询中心点函数
function getTrafficTarget() {
  // 票务中心默认坐标
  if (trafficTargetType.value === 'ticket') {
    return {
      name: '票务中心',
      lng: 111.65632,
      lat: 33.774569
    }
  }
  // 当前选中 POI
  if (trafficTargetType.value === 'selectedPoi') {
    if (!selectedPoi.value) {
      statusText.value = '请先选择一个 POI'
      return null
    }
    return {
      name: selectedPoi.value.name,
      lng: Number(selectedPoi.value.lng),
      lat: Number(selectedPoi.value.lat)
    }
  }
  // 地图点击位置
  if (trafficTargetType.value === 'mapClick') {
    if (!mapClickInfo.value) {
      statusText.value = '请先点击地图上的一个位置'
      return null
    }
    return {
      name: mapClickInfo.value.name || '地图点击位置',
      lng: Number(mapClickInfo.value.lng),
      lat: Number(mapClickInfo.value.lat)
    }
  }
  return null
}
//交通态势数据整理函数
function normalizeTrafficInfo(data) {
  if (!data) {
    return {
      targetName: '暂无',
      query_mode: 'unknown',
      matched_road: '暂无',
      radius: '暂无',
      used_radius: null,
      evaluation_description: '暂无交通态势数据',
      expedite: '暂无',
      congested: '暂无',
      blocked: '暂无',
      description: '当前区域暂无可用交通态势数据',
      amap_info: '暂无',
      amap_infocode: '暂无'
    }
  }

  return {
    targetName:
      data.targetName ||
      data.target_name ||
      data.name ||
      data.poi_name ||
      data.address ||
      '地图点击位置',

    query_mode:
      data.query_mode ||
      data.queryMode ||
      data.mode ||
      'circle',

    matched_road:
      data.matched_road ||
      data.matchedRoad ||
      data.road_name ||
      data.roadName ||
      '暂无',

    radius:
      data.radius ||
      data.query_radius ||
      data.selected_radius ||
      '暂无',

    used_radius:
      data.used_radius ||
      data.usedRadius ||
      data.actual_radius ||
      null,

    evaluation_description:
      data.evaluation_description ||
      data.evaluation ||
      data.traffic_evaluation ||
      data.status ||
      '暂无交通态势数据',

    expedite:
      data.expedite ||
      data.expedite_ratio ||
      data.smooth_ratio ||
      '暂无',

    congested:
      data.congested ||
      data.congested_ratio ||
      data.jam_ratio ||
      '暂无',

    blocked:
      data.blocked ||
      data.blocked_ratio ||
      '暂无',

    description:
      data.description ||
      data.desc ||
      data.traffic_description ||
      '当前区域暂无可用交通态势数据',

    amap_info:
      data.amap_info ||
      data.info ||
      data.amapInfo ||
      '暂无',

    amap_infocode:
      data.amap_infocode ||
      data.infocode ||
      data.amapInfocode ||
      '暂无'
  }
}
//查询交通态势函数
async function queryTrafficStatus() {
  const target = getTrafficTarget()

  if (!target) return

  try {
    const response = await fetch(
      `/api/traffic/circle?lng=${target.lng}&lat=${target.lat}&radius=${trafficRadius.value}`
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '交通态势接口请求失败')
    }

    const data = await response.json()
    trafficInfo.value = normalizeTrafficInfo(data, target)

    if (trafficCircleLayer) {
      map.removeLayer(trafficCircleLayer)
      trafficCircleLayer = null
    }

    trafficCircleLayer = L.circle([target.lat, target.lng], {
      radius: Number(trafficRadius.value),
      color: '#3498db',
      weight: 3,
      fillColor: '#3498db',
      fillOpacity: 0.08
    }).addTo(map)

    trafficCircleLayer.bindPopup(`
      <b>周边交通态势</b><br>
      查询对象：${target.name}<br>
      查询方式：${getTrafficQueryModeName(data.query_mode)}<br>
      匹配道路：${data.matched_road || '暂无'}<br>
      半径：${trafficRadius.value} 米<br>
      交通评价：${data.evaluation_description || '暂无'}<br>
      畅通比例：${data.expedite || '暂无'}<br>
      拥堵比例：${data.congested || '暂无'}<br>
      阻塞比例：${data.blocked || '暂无'}
    `)

    map.fitBounds(trafficCircleLayer.getBounds(), {
      padding: [40, 40]
    })

    if (data.success === false) {
      statusText.value = `交通态势查询完成，但当前区域暂无有效路况数据`
    } else {
      statusText.value = `交通态势查询完成：${target.name}`
    }
  } catch (error) {
    console.error(error)
    statusText.value = `交通态势查询失败：${error.message}`
  }
}
//清除交通态势函数
function clearTrafficStatus() {
  if (trafficCircleLayer) {
    map.removeLayer(trafficCircleLayer)
    trafficCircleLayer = null
  }
  trafficInfo.value = null
  statusText.value = '已清除交通态势查询结果'
}
//客流等级颜色函数
function getCrowdColor(level) {
  if (level === '拥挤') return '#e74c3c'
  if (level === '适中') return '#f39c12'
  return '#27ae60'
}
function getCrowdRadius(value) {
  const v = Number(value) || 0
  return 7 + Math.round(v / 15)
}
//统计客流摘要函数
function buildCrowdSummary(items) {
  const total = items.length

  const crowded = items.filter(item => item.crowd_level === '拥挤')
  const medium = items.filter(item => item.crowd_level === '适中')
  const comfortable = items.filter(item => item.crowd_level === '舒适')

  return {
    total,
    crowdedCount: crowded.length,
    mediumCount: medium.length,
    comfortableCount: comfortable.length,
    mostCrowded: crowded.slice(0, 3).map(item => item.poi_name)
  }
}
//加载模拟客流点
async function loadCrowdStatus() {
  try {
    const response = await fetch('/api/crowd/status')

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '模拟客流接口请求失败')
    }

    const data = await response.json()

    crowdList.value = data.items || []
    crowdSummary.value = buildCrowdSummary(crowdList.value)

    if (crowdLayer) {
      map.removeLayer(crowdLayer)
      crowdLayer = null
    }
    const geojson = {
      type: 'FeatureCollection',
      features: crowdList.value.map(item => ({
        type: 'Feature',
        properties: item,
        geometry: {
          type: 'Point',
          coordinates: [Number(item.lng), Number(item.lat)]
        }
      }))
    }
    crowdLayer = L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) => {
        const p = feature.properties
        const color = getCrowdColor(p.crowd_level)

        return L.circleMarker(latlng, {
          radius: getCrowdRadius(p.crowd_value),
          color,
          weight: 2,
          fillColor: color,
          fillOpacity: 0.75
        })
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties

        layer.bindPopup(`
          <b>${p.poi_name}</b><br>
          类型：${p.type || '暂无'} / ${p.subtype || '暂无'}<br>
          客流等级：${p.crowd_level}<br>
          客流指数：${p.crowd_value}<br>
          时间段：${p.time_slot || '暂无'}<br>
          更新时间：${p.update_time || '暂无'}<br>
          数据来源：${p.source || '系统模拟'}<br>
          说明：${p.remark || ''}
        `)
      }
    })
    if (layerVisible.crowd) {
      crowdLayer.addTo(map)
    }
    statusText.value = `模拟客流加载成功，共 ${crowdList.value.length} 个点`
  } catch (error) {
    console.error(error)
    statusText.value = `模拟客流加载失败：${error.message}`
  }
}
//生成新的模拟客流
async function simulateCrowd() {
  try {
    const response = await fetch(
      `/api/crowd/simulate?time_slot=${encodeURIComponent(crowdTimeSlot.value)}`,
      {
        method: 'POST'
      }
    )
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '生成模拟客流失败')
    }

    await response.json()
    await loadCrowdStatus()

    if (layerVisible.crowdHeat) {
      await loadCrowdHeatmap()
    }

    statusText.value = `已生成${crowdTimeSlot.value}模拟客流`
  } catch (error) {
    console.error(error)
    statusText.value = `生成模拟客流失败：${error.message}`
  }
}
//客流热力图函数
async function loadCrowdHeatmap() {
  try {
    const response = await fetch('/api/crowd/heatmap')

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '客流热力图接口请求失败')
    }
    const data = await response.json()
    const items = data.items || []
    if (crowdHeatLayer) {
      map.removeLayer(crowdHeatLayer)
      crowdHeatLayer = null
    }
    crowdHeatLayer = L.layerGroup()
    items.forEach(item => {
      const value = Number(item.crowd_value) || 0
      const color = getCrowdColor(item.crowd_level)

      const radius = 80 + value * 8

      const circle = L.circle([Number(item.lat), Number(item.lng)], {
        radius,
        color,
        weight: 1,
        fillColor: color,
        fillOpacity: 0.16,
        opacity: 0.35
      })
      circle.bindPopup(`
        <b>${item.poi_name}</b><br>
        热力值：${item.crowd_value}<br>
        客流等级：${item.crowd_level}
      `)
      crowdHeatLayer.addLayer(circle)
    })
    if (layerVisible.crowdHeat) {
      crowdHeatLayer.addTo(map)
    }

    statusText.value = `客流热力图加载成功，共 ${items.length} 个热力点`
  } catch (error) {
    console.error(error)
    statusText.value = `客流热力图加载失败：${error.message}`
  }
}
//清除客流热力图
function clearCrowdLayers() {
  if (crowdLayer) {
    map.removeLayer(crowdLayer)
    crowdLayer = null
  }
  if (crowdHeatLayer) {
    map.removeLayer(crowdHeatLayer)
    crowdHeatLayer = null
  }
  crowdList.value = []
  crowdSummary.value = null

  statusText.value = '已清除模拟客流和客流热力图'
}
//地图点击查询函数
async function handleMapClickQuery(e) {
  const lng = e.latlng.lng
  const lat = e.latlng.lat

  try {
    const response = await fetch(
      `/api/amap/regeo?lng=${lng}&lat=${lat}&radius=800`
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '地图点击查询失败')
    }

    const data = await response.json()

    const nearestPoi = data.pois && data.pois.length > 0
      ? data.pois[0]
      : null

    const clickPoi = {
      id: nearestPoi?.id || 'map-click-point',
      name: nearestPoi?.name || data.formatted_address || '地图点击位置',
      lng: nearestPoi?.lng || lng,
      lat: nearestPoi?.lat || lat,
      address: nearestPoi?.address || data.formatted_address || '',
      type: nearestPoi?.type || '地图点击位置',
      adcode: data.adcode,
      pname: data.province || '',
      cityname: data.city || '',
      adname: data.district || '',
      source: '地图点击'
    }

    mapClickInfo.value = clickPoi

    if (mapClickLayer) {
      map.removeLayer(mapClickLayer)
      mapClickLayer = null
    }

    mapClickLayer = L.circleMarker([clickPoi.lat, clickPoi.lng], {
      radius: 9,
      color: '#ff9800',
      weight: 3,
      fillColor: '#ff9800',
      fillOpacity: 0.75
    }).addTo(map)

    const uid = Date.now()

    const startBtnId = `map-click-start-${uid}`
    const endBtnId = `map-click-end-${uid}`
    const weatherBtnId = `map-click-weather-${uid}`
    const locateBtnId = `map-click-locate-${uid}`
    const clearBtnId = `map-click-clear-${uid}`

    const poiListHtml = data.pois && data.pois.length > 0
      ? data.pois.slice(0, 5).map((item, index) => {
          return `${index + 1}. ${item.name || '未命名'}（${item.distance || '--'}米）`
        }).join('<br>')
      : '暂无附近 POI'

    mapClickLayer.bindPopup(`
      <div class="map-click-popup">
        <b>${clickPoi.name}</b><br>
        地址：${clickPoi.address || '暂无'}<br>
        行政区：${clickPoi.pname || ''}${clickPoi.cityname || ''}${clickPoi.adname || ''}<br>
        adcode：${clickPoi.adcode || '暂无'}<br>
        经纬度：${Number(clickPoi.lng).toFixed(6)}, ${Number(clickPoi.lat).toFixed(6)}<br>
        <hr>
        <b>附近 POI：</b><br>
        ${poiListHtml}

        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
          <button id="${startBtnId}" style="padding:5px 8px;border:none;background:#2f80ed;color:white;border-radius:4px;cursor:pointer;">
            设为起点
          </button>
          <button id="${endBtnId}" style="padding:5px 8px;border:none;background:#27ae60;color:white;border-radius:4px;cursor:pointer;">
            设为终点
          </button>
          <button id="${weatherBtnId}" style="padding:5px 8px;border:none;background:#8e44ad;color:white;border-radius:4px;cursor:pointer;">
            查看此处天气
          </button>
          <button id="${locateBtnId}" style="padding:5px 8px;border:none;background:#f39c12;color:white;border-radius:4px;cursor:pointer;">
            定位到此处
          </button>
          <button id="${clearBtnId}" style="padding:5px 8px;border:none;background:#95a5a6;color:white;border-radius:4px;cursor:pointer;">
            清除查询
          </button>
        </div>
      </div>
    `)

    mapClickLayer.on('popupopen', () => {
      const startBtn = document.getElementById(startBtnId)
      const endBtn = document.getElementById(endBtnId)
      const weatherBtn = document.getElementById(weatherBtnId)
      const locateBtn = document.getElementById(locateBtnId)
      const clearBtn = document.getElementById(clearBtnId)

      if (startBtn) {
        startBtn.onclick = () => {
          setRouteStart(clickPoi)
        }
      }

      if (endBtn) {
        endBtn.onclick = () => {
          setRouteEnd(clickPoi)
        }
      }

      if (weatherBtn) {
        weatherBtn.onclick = () => {
          setWeatherTarget(clickPoi, true)
        }
      }

      if (locateBtn) {
        locateBtn.onclick = () => {
          map.flyTo([clickPoi.lat, clickPoi.lng], 16)
        }
      }

      if (clearBtn) {
        clearBtn.onclick = () => {
          clearMapClickQuery()
        }
      }
    })

    mapClickLayer.openPopup()

    setWeatherTarget(clickPoi, false)

    statusText.value = `已查询地图点击位置：${clickPoi.name}`
  } catch (error) {
    console.error(error)
    statusText.value = `地图点击查询失败：${error.message}`
  }
}
async function clearMapClickQuery() {
  // 清除地图点击查询点
  if (mapClickLayer) {
    map.removeLayer(mapClickLayer)
    mapClickLayer = null
  }

  mapClickInfo.value = null

  if (map) {
    map.closePopup()
  }
  // 如果当前天气跟随的是“地图点击”位置，则恢复为栾川县天气
  if (weatherTargetPoi.value && weatherTargetPoi.value.source === '地图点击') {
    weatherFollowSearch.value = false
    weatherTargetPoi.value = null
    await loadWeather('manual', defaultWeatherCity)
  }
  // 如果起点或终点来自地图点击，也一起清空
  if (routeStart.value && routeStart.value.source === '地图点击') {
    routeStart.value = null
  }

  if (routeEnd.value && routeEnd.value.source === '地图点击') {
    routeEnd.value = null
  }

  statusText.value = '已清除地图点击查询结果'
}
function isDistrictKeyword(keyword) {//判断行政区关键词的函数
  return (
    keyword.endsWith('省') ||
    keyword.endsWith('市') ||
    keyword.endsWith('区') ||
    keyword.endsWith('县')
  )
}
const lastOnlineSearchIsDistrict = ref(false)

function toggleOnlineDistrictPoiLayer() {
  // 只针对“行政区搜索”产生的在线 POI 点生效
  if (!lastOnlineSearchIsDistrict.value) {
    statusText.value = '该开关只影响行政区搜索时的在线 POI 点显示'
    return
  }
  if (!onlineSearchLayer) {
    statusText.value = '当前没有可切换的行政区 POI 点'
    return
  }
  if (layerVisible.onlineDistrictPoi) {
    onlineSearchLayer.addTo(map)
    statusText.value = '已显示行政区搜索 POI 点'
  } else {
    if (map.hasLayer(onlineSearchLayer)) {
      map.removeLayer(onlineSearchLayer)
    }
    statusText.value = '已隐藏行政区搜索 POI 点'
  }
}
//加载行政区边界函数
async function loadOnlineDistrictBoundary(keyword) {
  if (!keyword) return

  try {
    const response = await fetch(
      `/api/amap/district?keywords=${encodeURIComponent(keyword)}`
    )

    if (!response.ok) {
      return
    }

    const data = await response.json()

    if (
      !data.geojson ||
      !data.geojson.features ||
      data.geojson.features.length === 0
    ) {
      return
    }

    if (onlineDistrictLayer) {
      map.removeLayer(onlineDistrictLayer)
      onlineDistrictLayer = null
    }

    onlineDistrictLayer = L.geoJSON(data.geojson, {
      interactive: false,
      style: {
        color: '#00b894',
        weight: 3,
        fillColor: '#00b894',
        fillOpacity: 0.08
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties || {}

        if (p.name) {
          onlineDistrictName.value = p.name
        }
      }
    })

    if (layerVisible.onlineDistrict) {
      onlineDistrictLayer.addTo(map)
    }

    if (
      onlineDistrictLayer.getBounds &&
      onlineDistrictLayer.getBounds().isValid()
    ) {
      map.fitBounds(onlineDistrictLayer.getBounds(), {
        padding: [50, 50]
      })
    }

    statusText.value = `已加载在线行政区范围：${onlineDistrictName.value || keyword}`
  } catch (error) {
    console.error(error)
  }
}
//本地文件加载函数
function triggerLocalGeojsonInput() {
  if (localGeojsonInput.value) {
    localGeojsonInput.value.value = ''
    localGeojsonInput.value.click()
  }
}
function handleLocalGeojsonFile(event) {
  const file = event.target.files[0]
  if (!file) return
  const fileName = file.name.toLowerCase()
  if (!fileName.endsWith('.geojson') && !fileName.endsWith('.json')) {
    statusText.value = '请选择 GeoJSON 或 JSON 格式文件'
    return
  }

  const reader = new FileReader()

  reader.onload = (e) => {
    try {
      const geojson = JSON.parse(e.target.result)

      if (!geojson.type) {
        statusText.value = '文件不是有效的 GeoJSON 数据'
        return
      }

      if (localBoundaryLayer) {
        map.removeLayer(localBoundaryLayer)
        localBoundaryLayer = null
      }

      localBoundaryLayer = L.geoJSON(geojson, {
        style: {
          color: '#00a8ff',
          weight: 3,
          fillColor: '#00a8ff',
          fillOpacity: 0.08
        },
        onEachFeature: (feature, layer) => {
          const props = feature.properties || {}
          const name =
            props.name ||
            props.NAME ||
            props.Name ||
            props.adname ||
            props.fullname ||
            '本地边界数据'

          layer.bindPopup(`
            <b>${name}</b><br>
            数据来源：本地 GeoJSON 文件
          `)
        }
      }).addTo(map)

      if (
        localBoundaryLayer.getBounds &&
        localBoundaryLayer.getBounds().isValid()
      ) {
        map.fitBounds(localBoundaryLayer.getBounds(), {
          padding: [40, 40]
        })
      }

      localBoundaryName.value = file.name
      statusText.value = `本地边界文件加载成功：${file.name}`
    } catch (error) {
      console.error(error)
      statusText.value = '本地 GeoJSON 文件解析失败，请检查文件格式'
    }
  }
  reader.readAsText(file, 'utf-8')
}
//清除本地边界函数
function clearLocalBoundary() {
  if (localBoundaryLayer) {
    map.removeLayer(localBoundaryLayer)
    localBoundaryLayer = null
  }

  localBoundaryName.value = ''
  statusText.value = '已清除本地边界图层'
}
function resetMapViewToLuanchuan() {
  if (!map) return
  // 优先使用已经加载的栾川县边界范围
  if (
    boundaryLayer &&
    boundaryLayer.getBounds &&
    boundaryLayer.getBounds().isValid()
  ) {
    map.fitBounds(boundaryLayer.getBounds(), {
      padding: [40, 40],
      maxZoom: 11
    })
    return
  }
  // 如果边界图层还没加载，就回到栾川县附近默认中心
  map.flyTo([33.78, 111.62], 10)
}
async function clearOnlineSearchResults() {
  // 1. 清除在线搜索结果图层
  if (onlineSearchLayer) {
    map.removeLayer(onlineSearchLayer)
    onlineSearchLayer = null
  }
  if (onlineDistrictLayer) {
    map.removeLayer(onlineDistrictLayer)
    onlineDistrictLayer = null
  }
  onlineDistrictName.value = ''
  // 2. 清空搜索结果和搜索框
  onlineSearchResults.value = []
  onlineSearchKeyword.value = ''

  // 3. 关闭地图弹窗
  if (map) {
    map.closePopup()
  }

  // 4. 如果天气正在跟随搜索点，关闭跟随并恢复默认栾川县天气
  weatherFollowSearch.value = false
  weatherTargetPoi.value = null

  await loadWeather('manual', defaultWeatherCity)

  // 5. 如果起点/终点来自高德在线搜索，也一起清空，避免残留
  if (routeStart.value && routeStart.value.source === '高德在线搜索') {
    routeStart.value = null
  }

  if (routeEnd.value && routeEnd.value.source === '高德在线搜索') {
    routeEnd.value = null
  }

  // 6. 清除高德路径规划图层和摘要
  if (amapRouteLayer) {
    map.removeLayer(amapRouteLayer)
    amapRouteLayer = null
  }

  amapRouteSummary.value = null
  amapRouteMode.value = ''
  // 7. 地图视图恢复到栾川县
  resetMapViewToLuanchuan()

  statusText.value = '已清除在线搜索结果，恢复为栾川县天气，并返回栾川县地图范围'
}
async function getRegeoByLocation(lng, lat) {
  try {
    const response = await fetch(
      `/api/amap/regeo?lng=${lng}&lat=${lat}`
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '逆地理编码失败')
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error(error)
    statusText.value = '当前位置行政区信息获取失败'
    return null
  }
}
function getWeatherAdviceText() {
  const weather = weatherInfo.value.weather || '未知'
  const temperature = weatherInfo.value.temperature || '--'
  const wind = weatherInfo.value.wind || '--'
  const humidity = weatherInfo.value.humidity || '--'

  // 如果开启了跟随搜索点/当前位置天气，只显示基础天气信息，不显示路线建议
  if (weatherFollowSearch.value && weatherTargetPoi.value) {
    return `当前匹配点为 ${weatherTargetPoi.value.name}，所在区域天气为${weather}，气温约${temperature}℃，风力${wind}，湿度${humidity}%。`
  }

  // 默认栾川县天气，保留旅游建议
  return weatherInfo.value.advice || `当前天气为${weather}，气温约${temperature}℃，风力${wind}。`
}
//WGS84 转 GCJ-02 坐标函数
function outOfChina(lng, lat) {
  return lng < 72.004 || lng > 137.8347 || lat < 0.8293 || lat > 55.8271
}
function transformLat(lng, lat) {
  let ret =
    -100.0 +
    2.0 * lng +
    3.0 * lat +
    0.2 * lat * lat +
    0.1 * lng * lat +
    0.2 * Math.sqrt(Math.abs(lng))

  ret +=
    ((20.0 * Math.sin(6.0 * lng * Math.PI) +
      20.0 * Math.sin(2.0 * lng * Math.PI)) *
      2.0) /
    3.0

  ret +=
    ((20.0 * Math.sin(lat * Math.PI) +
      40.0 * Math.sin((lat / 3.0) * Math.PI)) *
      2.0) /
    3.0

  ret +=
    ((160.0 * Math.sin((lat / 12.0) * Math.PI) +
      320 * Math.sin((lat * Math.PI) / 30.0)) *
      2.0) /
    3.0

  return ret
}
function transformLng(lng, lat) {
  let ret =
    300.0 +
    lng +
    2.0 * lat +
    0.1 * lng * lng +
    0.1 * lng * lat +
    0.1 * Math.sqrt(Math.abs(lng))

  ret +=
    ((20.0 * Math.sin(6.0 * lng * Math.PI) +
      20.0 * Math.sin(2.0 * lng * Math.PI)) *
      2.0) /
    3.0

  ret +=
    ((20.0 * Math.sin(lng * Math.PI) +
      40.0 * Math.sin((lng / 3.0) * Math.PI)) *
      2.0) /
    3.0

  ret +=
    ((150.0 * Math.sin((lng / 12.0) * Math.PI) +
      300.0 * Math.sin((lng / 30.0) * Math.PI)) *
      2.0) /
    3.0

  return ret
}
function wgs84ToGcj02(lng, lat) {
  if (outOfChina(lng, lat)) {
    return [lng, lat]
  }

  const a = 6378245.0
  const ee = 0.00669342162296594323

  let dLat = transformLat(lng - 105.0, lat - 35.0)
  let dLng = transformLng(lng - 105.0, lat - 35.0)

  const radLat = (lat / 180.0) * Math.PI
  let magic = Math.sin(radLat)
  magic = 1 - ee * magic * magic

  const sqrtMagic = Math.sqrt(magic)

  dLat =
    (dLat * 180.0) /
    (((a * (1 - ee)) / (magic * sqrtMagic)) * Math.PI)

  dLng =
    (dLng * 180.0) /
    ((a / sqrtMagic) * Math.cos(radLat) * Math.PI)

  return [lng + dLng, lat + dLat]
}
function locateUser() {
  if (!navigator.geolocation) {
    statusText.value = '当前浏览器不支持定位功能'
    return
  }

  statusText.value = '正在请求浏览器定位权限...'

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const rawLng = position.coords.longitude
      const rawLat = position.coords.latitude
      const accuracy = position.coords.accuracy || 0

      const [lng, lat] = wgs84ToGcj02(rawLng, rawLat)

      // 通过高德逆地理编码获取当前位置 adcode
      const regeo = await getRegeoByLocation(lng, lat)

      const userPoi = {
        id: 'user-location',
        name: '我的当前位置',
        lng,
        lat,
        source: '浏览器定位',
        adcode: regeo?.adcode || null,
        pname: regeo?.province || '',
        cityname: regeo?.city || '',
        adname: regeo?.district || '',
        address: regeo?.formatted_address || ''
      }

      if (userLocationLayer) {
        map.removeLayer(userLocationLayer)
      }

      if (userAccuracyCircle) {
        map.removeLayer(userAccuracyCircle)
      }

      userAccuracyCircle = L.circle([lat, lng], {
        radius: accuracy,
        color: '#2f80ed',
        weight: 1,
        fillColor: '#2f80ed',
        fillOpacity: 0.08
      }).addTo(map)

      userLocationLayer = L.circleMarker([lat, lng], {
        radius: 9,
        color: '#2f80ed',
        weight: 3,
        fillColor: '#ffffff',
        fillOpacity: 1
      }).addTo(map)

      const startBtnId = 'user-location-start-btn'
      const weatherBtnId = 'user-location-weather-btn'

      userLocationLayer.bindPopup(`
        <b>我的当前位置</b><br>
        经度：${lng.toFixed(6)}<br>
        纬度：${lat.toFixed(6)}<br>
        定位精度：约 ${Math.round(accuracy)} 米<br>
        地址：${userPoi.address || '暂无'}<br>
        行政区：${userPoi.cityname || ''}${userPoi.adname || ''}<br>
        <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap;">
          <button id="${startBtnId}" style="padding:5px 10px;border:none;background:#2f80ed;color:white;border-radius:4px;cursor:pointer;">
            设为起点
          </button>
          <button id="${weatherBtnId}" style="padding:5px 10px;border:none;background:#8e44ad;color:white;border-radius:4px;cursor:pointer;">
            查看此处天气
          </button>
        </div>
      `)

      userLocationLayer.on('popupopen', () => {
        const startBtn = document.getElementById(startBtnId)
        const weatherBtn = document.getElementById(weatherBtnId)

        if (startBtn) {
          startBtn.onclick = () => {
            setRouteStart(userPoi)
          }
        }

        if (weatherBtn) {
          weatherBtn.onclick = () => {
            setWeatherTarget(userPoi, true)
          }
        }
      })

      map.flyTo([lat, lng], 15)
      userLocationLayer.openPopup()

      // 定位成功后，自动把当前位置作为天气匹配点，并切换天气
      if (userPoi.adcode) {
        setWeatherTarget(userPoi, true)
        statusText.value = '当前位置定位成功，并已切换为当前位置天气'
      } else {
        weatherTargetPoi.value = userPoi
        statusText.value = '当前位置定位成功，但未获取到天气行政区编码'
      }
    },
    (error) => {
      if (error.code === 1) {
        statusText.value = '定位失败：用户拒绝了位置权限'
      } else if (error.code === 2) {
        statusText.value = '定位失败：无法获取当前位置'
      } else if (error.code === 3) {
        statusText.value = '定位失败：定位超时'
      } else {
        statusText.value = '定位失败：未知错误'
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  )
}
function setWeatherTarget(poi, autoLoad = false) {
  if (!poi) {
    statusText.value = '未选择天气匹配点'
    return
  }

  weatherTargetPoi.value = poi
  if (autoLoad) {
    if (!poi.adcode) {
      statusText.value = '该点缺少 adcode，无法匹配天气'
      return
    }
    weatherFollowSearch.value = true
    loadWeather('follow', poi.adcode)
    statusText.value = `已切换为 ${poi.name} 所在区域天气`
  }
}
//重置函数
function resetSelectedPoi() {
  selectedPoi.value = null
  if (map) {
    map.closePopup()
  }
  statusText.value = '已重置景点详情'
}
//设置起终点
function setRouteStart(poi) {
  if (!poi || !poi.lng || !poi.lat) {
    statusText.value = '该点缺少经纬度，不能设为起点'
    return
  }

  routeStart.value = {
    id: poi.id || null,
    name: poi.name || '未命名地点',
    lng: Number(poi.lng),
    lat: Number(poi.lat),
    source: poi.source || '系统POI'
  }

  statusText.value = `已设置起点：${routeStart.value.name}`
}
function setRouteEnd(poi) {
  if (!poi || !poi.lng || !poi.lat) {
    statusText.value = '该点缺少经纬度，不能设为终点'
    return
  }

  routeEnd.value = {
    id: poi.id || null,
    name: poi.name || '未命名地点',
    lng: Number(poi.lng),
    lat: Number(poi.lat),
    source: poi.source || '系统POI'
  }

  statusText.value = `已设置终点：${routeEnd.value.name}`
}
function flyToOnlinePoi(poi) {
  if (!map || !poi || !poi.lng || !poi.lat) {
    statusText.value = '该在线点位缺少经纬度，无法定位'
    return
  }

  map.flyTo([Number(poi.lat), Number(poi.lng)], 16)

  setWeatherTarget(poi, false)
  saveUserRecord('poi_view', poi.name || '在线点位', {
  poi
  })
  statusText.value = `已定位到在线搜索点：${poi.name}`
}
//路径规划函数
async function planAmapRoute() {
  if (!routeStart.value || !routeEnd.value) {
    statusText.value = '请先设置起点和终点'
    return
  }
  if (!amapRouteMode.value) {
  statusText.value = '请选择路径规划方式'
  return
  }
  const origin = `${routeStart.value.lng},${routeStart.value.lat}`
  const destination = `${routeEnd.value.lng},${routeEnd.value.lat}`

  try {
    const response = await fetch(
      `/api/amap/route?origin=${origin}&destination=${destination}&mode=${amapRouteMode.value}`
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '路径规划接口请求失败')
    }

    const data = await response.json()

    if (!data.polyline || data.polyline.length === 0) {
      statusText.value = '未获取到有效路径，请检查起终点是否合理'
      return
    }

    if (amapRouteLayer) {
      map.removeLayer(amapRouteLayer)
    }

    const geojson = {
      type: 'Feature',
      properties: {
        mode: data.mode,
        distance: data.distance,
        duration: data.duration,
        startName: routeStart.value.name,
        endName: routeEnd.value.name
      },
      geometry: {
        type: 'LineString',
        coordinates: data.polyline
      }
    }

    amapRouteLayer = L.geoJSON(geojson, {
      style: {
        color: '#3498db',
        weight: 6,
        opacity: 0.9
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties

        const distanceKm = p.distance
          ? (p.distance / 1000).toFixed(2)
          : '--'

        const durationMin = p.duration
          ? Math.round(p.duration / 60)
          : '--'

        layer.bindPopup(`
          <b>高德路径规划</b><br>
          起点：${p.startName}<br>
          终点：${p.endName}<br>
          方式：${p.mode === 'walking' ? '步行' : '驾车'}<br>
          距离：${distanceKm} km<br>
          预计时间：${durationMin} 分钟
        `)
      }
    }).addTo(map)

    if (amapRouteLayer.getBounds && amapRouteLayer.getBounds().isValid()) {
      map.fitBounds(amapRouteLayer.getBounds(), {
        padding: [50, 50]
      })
    }

    amapRouteSummary.value = {
      modeText: amapRouteMode.value === 'walking' ? '步行路线' : '驾车路线',
      distanceText: data.distance ? `${(data.distance / 1000).toFixed(2)} km` : '--',
      durationText: data.duration ? `${Math.round(data.duration / 60)} 分钟` : '--'
    }

    statusText.value = `路径规划完成：${routeStart.value.name} → ${routeEnd.value.name}`
    saveUserRecord('route_plan', `${routeStart.value.name} → ${routeEnd.value.name}`, {
      start: routeStart.value,
      end: routeEnd.value,
      mode: amapRouteMode.value,
      summary: amapRouteSummary.value
    })
  } catch (error) {
    console.error(error)
    statusText.value = `高德路径规划失败：${error.message}`
  }
}
//清除路径函数
function clearAmapRoute() {
  if (amapRouteLayer) {
    map.removeLayer(amapRouteLayer)
    amapRouteLayer = null
  }

  routeStart.value = null
  routeEnd.value = null
  amapRouteMode.value = ''
  amapRouteSummary.value = null

  statusText.value = '已清除高德路径规划结果，并重置起点、终点和路线方式'
}
//搜索函数
async function searchOnlinePoi() {
  const keyword = onlineSearchKeyword.value.trim()

  if (!keyword) {
    statusText.value = '请输入在线地图搜索关键词'
    return
  }
  const isDistrict = isDistrictKeyword(keyword)
  lastOnlineSearchIsDistrict.value = isDistrict
  try {
    // 搜索新地点前，先清除旧的在线搜索结果图层和天气匹配状态
    if (onlineSearchLayer) {
      map.removeLayer(onlineSearchLayer)
      onlineSearchLayer = null
    }
    if (onlineDistrictLayer) {// 清除旧的在线行政区范围
      map.removeLayer(onlineDistrictLayer)
      onlineDistrictLayer = null
    }

    onlineSearchResults.value = []

    if (weatherTargetPoi.value && weatherTargetPoi.value.source === '高德在线搜索') {
      weatherFollowSearch.value = false
      weatherTargetPoi.value = null
      await loadWeather('manual', defaultWeatherCity)
    }

    if (map) {
      map.closePopup()
    }
    // 行政区搜索：如果关闭 POI 点显示，只显示行政区范围
    if (isDistrict && !layerVisible.onlineDistrictPoi) {
      await loadOnlineDistrictBoundary(keyword)
      statusText.value = `已加载行政区范围：${keyword}`
      saveUserRecord('online_search', keyword, {
        keyword,
        isDistrict: true,
        result_count: 0,
        mode: 'district_boundary_only'
      })
      return
    }
    const response = await fetch(
      `/api/amap/search?keywords=${encodeURIComponent(keyword)}`
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '在线地图搜索接口请求失败')
    }

    const data = await response.json()

    onlineSearchResults.value = data.pois || []

    if (onlineSearchLayer) {
      map.removeLayer(onlineSearchLayer)
    }

    const now = Date.now()

    const geojson = {
      type: 'FeatureCollection',
      features: onlineSearchResults.value.map((item, index) => ({
        type: 'Feature',
        properties: {
          ...item,
          uid: `online-poi-${now}-${index}`
        },
        geometry: {
          type: 'Point',
          coordinates: [item.lng, item.lat]
        }
      }))
    }

    onlineSearchLayer = L.geoJSON(geojson, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, {
          radius: 8,
          color: '#8e44ad',
          weight: 2,
          fillColor: '#9b59b6',
          fillOpacity: 0.85
        })
      },

      onEachFeature: (feature, layer) => {
        const p = feature.properties

        const startBtnId = `${p.uid}-start`
        const endBtnId = `${p.uid}-end`
        const locateBtnId = `${p.uid}-locate`

        // 1. 点位名称常驻显示
        layer.bindTooltip(p.name || '未命名地点', {
          permanent: true,
          direction: 'top',
          offset: [0, -10],
          className: 'online-poi-label'
        })

        // 2. 点击点位显示详细信息
        layer.bindPopup(`
          <div class="online-poi-popup">
            <b>${p.name || '未命名地点'}</b><br>
            类型：${p.type || '暂无'}<br>
            地址：${p.address || '暂无'}<br>
            区域：${p.pname || ''}${p.cityname || ''}${p.adname || ''}<br>
            经纬度：${p.lng}, ${p.lat}<br>

            <div style="margin-top:8px;display:flex;gap:6px;">
              <button id="${startBtnId}" style="padding:5px 8px;border:none;background:#2f80ed;color:white;border-radius:4px;cursor:pointer;">
                设为起点
              </button>
              <button id="${endBtnId}" style="padding:5px 8px;border:none;background:#27ae60;color:white;border-radius:4px;cursor:pointer;">
                设为终点
              </button>
              <button id="${locateBtnId}" style="padding:5px 8px;border:none;background:#8e44ad;color:white;border-radius:4px;cursor:pointer;">
                定位到此处
              </button>
            </div>
          </div>
        `)

        layer.on('popupopen', () => {
          const startBtn = document.getElementById(startBtnId)
          const endBtn = document.getElementById(endBtnId)
          const locateBtn = document.getElementById(locateBtnId)

          const poi = {
            id: p.id,
            name: p.name || '未命名地点',
            lng: Number(p.lng),
            lat: Number(p.lat),
            address: p.address,
            type: p.type,
            adcode: p.adcode,
            pname: p.pname,
            cityname: p.cityname,
            adname: p.adname,
            source: '高德在线搜索'
          }

          if (startBtn) {
            startBtn.onclick = () => {
              setRouteStart(poi)
            }
          }

          if (endBtn) {
            endBtn.onclick = () => {
              setRouteEnd(poi)
            }
          }

          if (locateBtn) {
            locateBtn.onclick = () => {
              flyToOnlinePoi(poi)
            }
          }
        })
        //3.点击搜索结果点位时，可以设置天气候选点
        layer.on('click', () => {
          weatherTargetPoi.value = {
            id: p.id,
            name: p.name || '未命名地点',
            lng: Number(p.lng),
            lat: Number(p.lat),
            address: p.address,
            type: p.type,
            adcode: p.adcode,
            pname: p.pname,
            cityname: p.cityname,
            adname: p.adname,
            source: '高德在线搜索'
          }
        })
      }
    }).addTo(map)

    if (onlineSearchLayer.getBounds && onlineSearchLayer.getBounds().isValid()) {
      map.fitBounds(onlineSearchLayer.getBounds(), {
        padding: [50, 50]
      })
    }
    // 如果搜索的是行政区，并且开启了 POI 点显示：
    // 先显示 POI，再叠加行政区范围，最终视图以行政区范围为主
    if (isDistrict) {
      await loadOnlineDistrictBoundary(keyword)
    }

    statusText.value = isDistrict
      ? `已加载行政区范围及 POI 点：${keyword}`
      : `在线地图搜索完成，共 ${onlineSearchResults.value.length} 个结果`

    saveUserRecord('online_search', keyword, {
      keyword,
      isDistrict,
      result_count: onlineSearchResults.value.length,
      results: onlineSearchResults.value.slice(0, 10)
    })

    if (isDistrict) {
      await loadOnlineDistrictBoundary(keyword)
    }
  } catch (error) {
    console.error(error)
    statusText.value = `在线地图搜索失败：${error.message}`
  }
}
//图层切换函数
function setLayerVisible(layer, visible) {
  if (!map || !layer) return

  if (visible) {
    if (!map.hasLayer(layer)) {
      layer.addTo(map)
    }
  } else {
    if (map.hasLayer(layer)) {
      map.removeLayer(layer)
    }
  }
}

function toggleLayer(type) {
  //if (type === 'boundary') {
  //  setLayerVisible(boundaryLayer, layerVisible.boundary)
  //}
  if (type === 'boundary') {
    if (layerVisible.boundary) {
      if (boundaryLayer) {
        boundaryLayer.addTo(map)
      } else {
        loadBoundary()
      }
    } else {
      if (boundaryLayer && map.hasLayer(boundaryLayer)) {
        map.removeLayer(boundaryLayer)
      }
    }
  }
  //if (type === 'poi') {
  //  setLayerVisible(poiLayer, layerVisible.poi)
  //}
  if (type === 'poi') {
    if (layerVisible.poi) {
      if (poiLayer) {
        poiLayer.addTo(map)
      } else {
        loadPois()
      }
    } else {
      if (poiLayer && map.hasLayer(poiLayer)) {
        map.removeLayer(poiLayer)
      }
    }
  }
  if (type === 'nearby') {
    setLayerVisible(nearbyLayer, layerVisible.nearby)
    setLayerVisible(nearbyCircle, layerVisible.nearby)
  }

  if (type === 'route') {
    setLayerVisible(routeLayer, layerVisible.route)
  }
  
  if (type === 'onlineDistrict') {
    setLayerVisible(onlineDistrictLayer, layerVisible.onlineDistrict)
  }
}
function toggleCrowdLayer() {
  if (!crowdLayer) {//模拟客流
    if (layerVisible.crowd) loadCrowdStatus()
    return
  }
  if (layerVisible.crowd) {
    crowdLayer.addTo(map)
  } else {
    map.removeLayer(crowdLayer)
  }
}
function toggleCrowdHeatLayer() {
  if (!crowdHeatLayer) {//客流热力图
    if (layerVisible.crowdHeat) loadCrowdHeatmap()
    return
  }
  if (layerVisible.crowdHeat) {
    crowdHeatLayer.addTo(map)
  } else {
    map.removeLayer(crowdHeatLayer)
  }
}
function initMap() {
  map = L.map('map', {
    center: [33.78, 111.62],
    zoom: 10,
    zoomControl: true
  })
  // 高德普通道路地图
  normalLayer = L.tileLayer(
    'https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
    {
      subdomains: ['1', '2', '3', '4'],
      maxZoom: 18,
      attribution: '© 高德地图'
    }
  )
  // 高德遥感影像
  satelliteLayer = L.tileLayer(
    'https://webst0{s}.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}',
    {
      subdomains: ['1', '2', '3', '4'],
      maxZoom: 18,
      attribution: '© 高德地图'
    }
  )
  // 高德影像路网标注
  satelliteRoadLayer = L.tileLayer(
    'https://webst0{s}.is.autonavi.com/appmaptile?style=8&x={x}&y={y}&z={z}',
    {
      subdomains: ['1', '2', '3', '4'],
      maxZoom: 18,
      attribution: '© 高德地图'
    }
  )

  normalLayer.addTo(map)
  currentBaseMap.value = 'normal'

  statusText.value = '地图初始化完成，当前为普通地图'
  map.on('click', handleMapClickQuery)
}
//底图切换函数
function removeAllBaseLayers() {
  if (normalLayer && map.hasLayer(normalLayer)) {
    map.removeLayer(normalLayer)
  }
  if (satelliteLayer && map.hasLayer(satelliteLayer)) {
    map.removeLayer(satelliteLayer)
  }
  if (satelliteRoadLayer && map.hasLayer(satelliteRoadLayer)) {
    map.removeLayer(satelliteRoadLayer)
  }
}
function switchBaseMap(type) {
  if (!map) return

  removeAllBaseLayers()
  if (type === 'normal') {
    normalLayer.addTo(map)
    currentBaseMap.value = 'normal'
    statusText.value = '已切换为普通地图'
  }
  if (type === 'satellite') {
    satelliteLayer.addTo(map)
    currentBaseMap.value = 'satellite'
    statusText.value = '已切换为遥感影像'
  }
  if (type === 'satelliteRoad') {
    satelliteLayer.addTo(map)
    satelliteRoadLayer.addTo(map)
    currentBaseMap.value = 'satelliteRoad'
    statusText.value = '已切换为影像路网地图'
  }
}
//边界加载函数
async function loadBoundary() {
  try {
    const response = await fetch('/api/boundary/luanchuan')
    const data = await response.json()

    if (boundaryLayer) {
      map.removeLayer(boundaryLayer)
    }

    boundaryLayer = L.geoJSON(data, {
      interactive: false,
      style: {
        color: '#ff6600',
        weight: 3,
        fillColor: '#ffcc66',
        fillOpacity: 0.12
      },
      onEachFeature: (feature, layer) => {
        const name = feature.properties.name || '栾川县'
        const adcode = feature.properties.adcode || ''
        layer.bindPopup(`
          <b>${name}</b><br>
          行政区划代码：${adcode}
        `)
      }
    })
    if (layerVisible.boundary) {
      boundaryLayer.addTo(map)
    }
    layerVisible.boundary = true

    map.fitBounds(boundaryLayer.getBounds())
    statusText.value = '栾川县边界加载成功'
  } catch (error) {
    console.error(error)
    statusText.value = '栾川县边界加载失败，请检查后端接口'
  }
}

async function loadPois(type = '') {
  try {
    currentType.value = type

    const params = new URLSearchParams()

    if (type) {
      params.append('type', type)
    }

    if (searchKeyword.value.trim()) {
      params.append('keyword', searchKeyword.value.trim())
    }

    let url = '/api/pois'
    const queryString = params.toString()

    if (queryString) {
      url += `?${queryString}`
    }

    const response = await fetch(url)
    const data = await response.json()

    if (poiLayer) {
      map.removeLayer(poiLayer)
    }

    poiList.value = data.features.map(feature => {
      const coords = feature.geometry.coordinates
      return {
        ...feature.properties,
        lng: coords[0],
        lat: coords[1]
      }
    })

    poiLayer = L.geoJSON(data, {
      pointToLayer: (feature, latlng) => {
        const poiType = feature.properties.type

        let color = '#2f80ed'
        if (poiType === 'attraction') color = '#e74c3c'
        if (poiType === 'transport') color = '#27ae60'
        if (poiType === 'service') color = '#f39c12'

        return L.circleMarker(latlng, {
          radius: 8,
          color: color,
          weight: 2,
          fillColor: color,
          fillOpacity: 0.75
        })
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties
        const coords = feature.geometry.coordinates

        const poi = {
          ...p,
          lng: coords[0],
          lat: coords[1]
        }

        layer.bindPopup(`
          <b>${p.name || ''}</b><br>
          类型：${p.type || ''}<br>
          子类型：${p.subtype || ''}<br>
          地址：${p.address || ''}<br>
          简介：${p.description || ''}
        `)

        layer.on('click', () => {
          selectedPoi.value = poi
          statusText.value = `已选中：${poi.name}`
        })
      }
    })
    if (layerVisible.poi) {
      poiLayer.addTo(map)
    }
    layerVisible.poi = true

    const typeText = type ? `，类型为 ${type}` : ''
    const keywordText = searchKeyword.value.trim()
      ? `，关键词为“${searchKeyword.value.trim()}”`
      : ''

    statusText.value = `POI 查询成功${typeText}${keywordText}，共 ${poiList.value.length} 个`
  } catch (error) {
    console.error(error)
    statusText.value = 'POI 查询失败，请检查后端接口'
  }
}
// 重置函数
function resetPois() {
  searchKeyword.value = ''
  currentType.value = ''
  loadPois('')
}

function flyToPoi(poi) {
  if (!map || !poi.lat || !poi.lng) return

  selectedPoi.value = poi

  map.flyTo([poi.lat, poi.lng], 15)

  L.popup()
    .setLatLng([poi.lat, poi.lng])
    .setContent(`
      <b>${poi.name}</b><br>
      类型：${poi.type || ''}<br>
      子类型：${poi.subtype || ''}<br>
      简介：${poi.description || ''}
    `)
    .openOn(map)

  statusText.value = `已选中：${poi.name}`
  saveUserRecord('poi_view', poi.name || '系统 POI', {
    poi
  })
}
//类型名称转换函数
function getTypeName(type) {
  const map = {
    attraction: '景点',
    transport: '交通 / 索道',
    service: '服务设施',
    route: '路线节点'
  }

  return map[type] || type || '未知类型'
}

function getSubTypeName(subtype) {
  const map = {
    scenic_area: '景区',
    natural: '自然景观',
    culture: '文化景观',
    viewpoint: '观景点',
    route_node: '游览节点',
    cableway: '索道',
    ticket: '票务服务',
    parking: '停车场',
    toilet: '厕所',
    restaurant: '餐饮',
    hotel: '住宿',
    visitor_center: '游客中心'
  }

  return map[subtype] || subtype || '未知子类型'
}
//附近查询函数
async function queryNearbyServices() {
  if (!selectedPoi.value) {
    statusText.value = '请先选择一个 POI'
    return
  }

  try {
    const params = new URLSearchParams()
    params.append('lng', selectedPoi.value.lng)
    params.append('lat', selectedPoi.value.lat)
    params.append('radius', nearbyRadius.value)
    params.append('type', 'service')
    params.append('exclude_id', selectedPoi.value.id)

    const url = `/api/pois/nearby?${params.toString()}`
    const response = await fetch(url)
    const data = await response.json()

    nearbyList.value = data.features.map(feature => {
      const coords = feature.geometry.coordinates
      return {
        ...feature.properties,
        lng: coords[0],
        lat: coords[1]
      }
    })

    if (nearbyLayer) {
      map.removeLayer(nearbyLayer)
    }

    if (nearbyCircle) {
      map.removeLayer(nearbyCircle)
    }

    nearbyCircle = L.circle([selectedPoi.value.lat, selectedPoi.value.lng], {
      radius: Number(nearbyRadius.value),
      color: '#8e44ad',
      weight: 2,
      fillColor: '#8e44ad',
      fillOpacity: 0.08
    })

    nearbyLayer = L.geoJSON(data, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, {
          radius: 9,
          color: '#8e44ad',
          weight: 2,
          fillColor: '#8e44ad',
          fillOpacity: 0.8
        })
      },
      onEachFeature: (feature, layer) => {
        const p = feature.properties
        layer.bindPopup(`
          <b>${p.name || ''}</b><br>
          类型：${p.type || ''}<br>
          子类型：${p.subtype || ''}<br>
          距离：${p.distance_m || ''} 米<br>
          简介：${p.description || ''}
        `)
      }
    })
    if (layerVisible.nearby) {
     nearbyCircle.addTo(map)
     nearbyLayer.addTo(map)
    }

    statusText.value = `已查询 ${selectedPoi.value.name} 附近 ${nearbyRadius.value} 米内服务设施，共 ${nearbyList.value.length} 个`
  } catch (error) {
    console.error(error)
    statusText.value = '附近服务查询失败'
  }
}
//清除函数
function clearNearby() {
  if (nearbyLayer) {
    map.removeLayer(nearbyLayer)
    nearbyLayer = null
  }

  if (nearbyCircle) {
    map.removeLayer(nearbyCircle)
    nearbyCircle = null
  }

  nearbyList.value = []
  statusText.value = '已清除附近查询结果'
}
//路线模板函数
async function loadRoutes() {
  try {
    const response = await fetch('/api/routes')
    const data = await response.json()

    routeList.value = data.routes || []
    statusText.value = `路线模板加载成功，共 ${routeList.value.length} 条`
  } catch (error) {
    console.error(error)
    statusText.value = '路线模板加载失败'
  }
}
//路线颜色函数
function getRouteColor(difficulty) {
  if (difficulty === 'easy') return '#16a085'      // 初阶：绿色
  if (difficulty === 'medium') return '#f39c12'    // 中阶：橙色
  if (difficulty === 'hard') return '#e74c3c'      // 高阶：红色
  return '#2f80ed'
}
//显示路线函数
async function showRoute(routeId) {
  try {
    const response = await fetch(`/api/routes/${routeId}/geojson`)
    const data = await response.json()

    selectedRoute.value = data.route

    if (routeLayer) {
      map.removeLayer(routeLayer)
    }

    const routeColor = getRouteColor(data.route.difficulty)

    routeLayer = L.geoJSON(data.geojson, {
      style: (feature) => {
        if (feature.geometry.type === 'LineString') {
          return {
            color: routeColor,
            weight: 5,
            opacity: 0.9
          }
        }

        return {}
      },

      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, {
          radius: 9,
          color: routeColor,
          weight: 2,
          fillColor: routeColor,
          fillOpacity: 0.9
        })
      },

      onEachFeature: (feature, layer) => {
        const p = feature.properties

        if (p.feature_type === 'route_node') {
          // 点击节点时仍然可以查看详细信息
          layer.bindPopup(`
            <b>${p.order}. ${p.name}</b><br>
            类型：${p.type || ''}<br>
            子类型：${p.subtype || ''}<br>
            简介：${p.description || ''}
          `)

          // 点击路线后，路线节点名称直接常驻显示
          layer.bindTooltip(`${p.order}. ${p.name}`, {
            permanent: true,
            direction: 'top',
            offset: [0, -10],
            className: `route-node-label route-${data.route.difficulty}`
          })
        }

        if (p.feature_type === 'route_line') {
          layer.bindPopup(`
            <b>${p.route_name}</b><br>
            难度：${p.difficulty || ''}<br>
            说明：该折线表示推荐游览节点顺序，不代表精确道路导航路径。
          `)
        }
      }
    })
    if (layerVisible.route) {
      routeLayer.addTo(map)
    }

    if (routeLayer.getBounds && routeLayer.getBounds().isValid()) {
      map.fitBounds(routeLayer.getBounds(), {
        padding: [40, 40]
      })
    }

    if (data.missing_nodes && data.missing_nodes.length > 0) {
      statusText.value = `路线加载成功，但有节点未匹配：${data.missing_nodes.join('、')}`
    } else {
      statusText.value = `已加载${data.route.route_name}`
    }
  } catch (error) {
    console.error(error)
    statusText.value = '路线加载失败，请检查路线接口'
  }
}
//清除路线函数
function clearRoute() {
  if (routeLayer) {
    map.removeLayer(routeLayer)
    routeLayer = null
  }

  selectedRoute.value = null
  statusText.value = '已清除路线'
}
//小助手发送问题函数
async function sendAssistantQuestion() {
  const question = assistantQuestion.value.trim()

  if (!question) {
    statusText.value = '请输入旅游问题'
    return
  }

  assistantMessages.value.push({
    role: 'user',
    content: question
  })

  assistantQuestion.value = ''

  try {
    const response = await fetch('/api/agent/travel', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question,
        agent_type: activeAgentType.value
      })
    })

    const data = await response.json().catch(() => null)

    if (!response.ok) {
      throw new Error(
        data?.detail ||
        data?.message ||
        `HTTP ${response.status}`
      )
    }

    assistantMessages.value.push({
      role: 'assistant',
      content: data?.answer || '暂无回答',
      meta: {
        agent_name: data?.agent_name || '综合旅游 Agent',
        agent_type: data?.agent_type || data?.planned_agent_type || 'comprehensive',
        tool_used: data?.tool_used || false,
        used_tools: data?.used_tools || [],
        map_action: data?.map_action || null,
        mode: data?.mode || ''
      }
    })

    if (data?.map_action) {
      applyAgentMapAction(data.map_action)
    }

    statusText.value = '智谱 AI 旅游小助手回答完成'

    saveUserRecord('assistant_chat', question, {
      question,
      answer: data?.answer || '暂无回答',
      agent_name: data?.agent_name || '综合旅游 Agent',
      agent_type: data?.agent_type || data?.planned_agent_type || activeAgentType.value,
      used_tools: data?.used_tools || [],
      map_action: data?.map_action || null
    })
  } catch (error) {
    console.error('Agent 调用失败：', error)

    assistantMessages.value.push({
      role: 'assistant',
      content: `智谱 AI Agent 调用失败：${error.message}`
    })

    statusText.value = `智谱 AI Agent 调用失败：${error.message}`
  }
}
//小助手发送路线问题函数
function applyAgentMapAction(action) {
  if (!action || action.type === 'none') return

  if (action.type === 'show_crowd_heatmap') {
    layerVisible.crowdHeat = true
    loadCrowdHeatmap()
    statusText.value = 'Agent 已打开客流热力图'
  }
  if (action.type === 'show_crowd_layer') {
    layerVisible.crowd = true
    loadCrowdStatus()
    statusText.value = 'Agent 已打开模拟客流图层'
  }
  if (action.type === 'open_dynamic_route_panel') {
    statusText.value = 'Agent 建议查看动态路线推荐模块'
  }
  if (action.type === 'open_traffic_panel') {
    statusText.value = 'Agent 建议查看周边交通态势模块'
  }
  if (action.type === 'show_weather_card') {
    weatherPanelOpen.value = true
    statusText.value = 'Agent 已展开天气卡片'
  }
}
//langchainDemo测试函数
async function runLangChainDemo() {
  const question = langchainDemoInput.value.trim()

  if (!question) {
    statusText.value = '请输入 LangChain Demo 测试问题'
    return
  }

  try {
    langchainDemoLoading.value = true
    langchainDemoResult.value = ''

    const response = await fetch('/api/langchain/demo', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question
      })
    })

    const data = await response.json().catch(() => null)

    if (!response.ok) {
      throw new Error(
        data?.detail ||
        data?.message ||
        `HTTP ${response.status}`
      )
    }

    langchainDemoResult.value =
      data?.answer ||
      data?.result ||
      data?.message ||
      'LangChain Demo 暂未生成有效回答'

    statusText.value = 'LangChain Demo 测试完成'
  } catch (error) {
    console.error('LangChain Demo 调用失败：', error)
    langchainDemoResult.value = `LangChain Demo 调用失败：${error.message}`
    statusText.value = `LangChain Demo 调用失败：${error.message}`
  } finally {
    langchainDemoLoading.value = false
  }
}
//天气调用函数
async function loadWeather(source = 'auto', cityCode = defaultWeatherCity) {
  try {
    const response = await fetch(
      `/api/weather/luanchuan?city=${encodeURIComponent(cityCode)}&t=${Date.now()}`,
      {
        cache: 'no-store'
      }
    )

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '天气接口请求失败')
    }

    const data = await response.json()

    weatherInfo.value = {
      city: data.city || '栾川县',
      weather: data.weather || '未知',
      temperature: data.temperature || '--',
      wind: `${data.winddirection || ''}风 ${data.windpower || ''}`,
      humidity: data.humidity || '--',
      reporttime: data.reporttime || '',
      fetched_at: data.fetched_at || '',
      advice: data.advice || '暂无旅游建议'
    }

    if (source === 'manual') {
      statusText.value = '手动刷新天气成功'
    } else if (source === 'follow') {
      statusText.value = '已切换为搜索点所在区域天气'
    } else {
      statusText.value = '实时天气加载成功'
    }
  } catch (error) {
    console.error(error)

    weatherInfo.value = {
      city: '栾川县',
      weather: '加载中',
      temperature: '--',
      wind: '--',
      humidity: '--',
      reporttime: '',
      fetched_at: '',
      advice: '天气信息加载失败，请检查后端天气接口或高德 Key。'
    }
    statusText.value = '天气信息加载失败'
  }
}
//开关处理函数
function toggleWeatherFollow() {
  if (weatherFollowSearch.value) {
    if (!weatherTargetPoi.value) {
      weatherFollowSearch.value = false
      statusText.value = '请先点击一个在线搜索结果点，或定位当前位置'
      return
    }

    if (!weatherTargetPoi.value.adcode) {
      weatherFollowSearch.value = false
      statusText.value = '该点位缺少 adcode，无法匹配天气'
      return
    }

    loadWeather('follow', weatherTargetPoi.value.adcode)
  } else {
    loadWeather('manual', defaultWeatherCity)
    statusText.value = '已恢复为栾川县天气'
  }
}
//天气图标函数
function getWeatherIcon(weather) {
  const w = weather || ''

  if (w.includes('雷')) return '⛈️'
  if (w.includes('雪')) return '❄️'
  if (w.includes('雨')) return '🌧️'
  if (w.includes('阴')) return '☁️'
  if (w.includes('多云')) return '⛅'
  if (w.includes('晴')) return '☀️'
  if (w.includes('雾') || w.includes('霾') || w.includes('沙')) return '🌫️'

  return '🌤️'
}

function getWeatherClass(weather) {
  const w = weather || ''

  if (w.includes('雷')) return 'weather-thunder'
  if (w.includes('雪')) return 'weather-snow'
  if (w.includes('雨')) return 'weather-rain'
  if (w.includes('阴')) return 'weather-cloudy'
  if (w.includes('多云')) return 'weather-cloudy'
  if (w.includes('晴')) return 'weather-sunny'
  if (w.includes('雾') || w.includes('霾') || w.includes('沙')) return 'weather-fog'

  return 'weather-default'
}
</script>

<style scoped>
.map-page {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 360px;
  min-width: 360px;
  height: 100vh;
  padding: 16px;
  background: #f8f8f8;
  border-right: 1px solid #ddd;
  box-sizing: border-box;
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar h2 {
  font-size: 20px;
  margin: 0 0 10px 0;
  text-align: center;
}

.sidebar h3 {
  font-size: 16px;
  margin: 18px 0 8px 0;
}

.sidebar p {
  font-size: 14px;
  color: #555;
  margin: 8px 0;
}

.sidebar button {
  width: 100%;
  padding: 10px;
  margin-top: 10px;
  background: #2f80ed;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.sidebar button:hover {
  background: #1c63c7;
}

.filter-box,
.info-box,
.poi-list {
  width: 100%;
  box-sizing: border-box;
}

.filter-box {
  margin-top: 16px;
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.filter-box h3 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
}

.info-box {
  margin-top: 16px;
  padding: 10px;
  background: white;
  border-radius: 6px;
  border: 1px solid #ddd;
}

.poi-list {
  margin-top: 12px;
}

.poi-item {
  width: 100%;
  padding: 10px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.poi-item:hover {
  background: #eef5ff;
}

.poi-item b {
  display: block;
  font-size: 14px;
}

.poi-item span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #777;
}

/* POI 搜索框样式 */
.search-box {
  margin-top: 16px;
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.search-box h3 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 9px;
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
  font-size: 14px;
}

.search-input:focus {
  border-color: #2f80ed;
}

.button-row {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.button-row button {
  flex: 1;
  width: auto;
  margin-top: 0;
}

/*附近查询样式 */
.nearby-box {
  margin-top: 16px;
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.nearby-box h3 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
}

.select-input {
  width: 100%;
  padding: 9px;
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
  font-size: 14px;
}

.nearby-list {
  margin-top: 10px;
}

.nearby-item {
  padding: 8px;
  margin-bottom: 8px;
  background: #fafafa;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.nearby-item:hover {
  background: #f1eaff;
}

.nearby-item b {
  display: block;
  font-size: 14px;
}

.nearby-item span {
  display: block;
  margin-top: 3px;
  font-size: 12px;
  color: #666;
}
/*路线查询样式 */
.route-box {
  margin-top: 16px;
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.route-box h3 {
  margin-top: 0;
  margin-bottom: 8px;
  font-size: 16px;
}

.route-item {
  padding: 9px;
  margin-bottom: 8px;
  background: #fafafa;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.route-item:hover {
  background: #e8f8f5;
}

.route-item b {
  display: block;
  font-size: 14px;
}

.route-item span {
  display: block;
  margin-top: 3px;
  font-size: 12px;
  color: #666;
}

.route-detail {
  margin-top: 10px;
  padding: 10px;
  background: #f7fffc;
  border: 1px solid #cceee5;
  border-radius: 6px;
}

.route-detail h4 {
  margin: 0 0 8px 0;
  font-size: 15px;
}

.route-detail p {
  font-size: 13px;
  line-height: 1.6;
  margin: 4px 0;
}
/*路线节点名称样式 */
:deep(.route-node-label) {
  background: rgba(255, 255, 255, 0.94);
  font-size: 12px;
  font-weight: bold;
  padding: 3px 6px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
}

:deep(.route-easy) {
  border: 1px solid #16a085;
  color: #0e6655;
}

:deep(.route-medium) {
  border: 1px solid #f39c12;
  color: #9a5b00;
}

:deep(.route-hard) {
  border: 1px solid #e74c3c;
  color: #922b21;
}
/**简洁样式 */
.panel-box {
  margin-top: 16px;
  padding: 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
}

.panel-box summary {
  cursor: pointer;
  font-weight: bold;
  font-size: 16px;
  color: #333;
  user-select: none;
}
.detail-panel {
  margin-top: 16px;
}
.detail-box {
  margin-top: 10px;
}
.reset-btn {
  width: 100%;
  padding: 9px;
  margin-top: 10px;
  background: #95a5a6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.reset-btn:hover {
  background: #7f8c8d;
}
.poi-panel {
  margin-top: 16px;
}

.poi-list {
  margin-top: 10px;
  max-height: 360px;
  overflow-y: auto;
}

.poi-item {
  width: 100%;
  padding: 10px;
  margin-bottom: 8px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
}

.poi-item:hover {
  background: #eef5ff;
}

.poi-item b {
  display: block;
  font-size: 14px;
}

.poi-item span {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: #777;
}

.control-group {
  margin-top: 12px;
}

.control-title {
  font-size: 14px;
  font-weight: bold;
  color: #555;
  margin-bottom: 6px;
}

.layer-check {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #444;
  margin: 8px 0;
  cursor: pointer;
}

.layer-check input {
  cursor: pointer;
}

.button-row {
  display: flex;
  gap: 8px;
  margin-top: 10px;
}

.button-row button {
  flex: 1;
  width: auto;
  margin-top: 0;
}
.map-wrapper {
  position: relative;
  flex: 1;
  height: 100vh;
  min-width: 0;
}

#map {
  width: 100%;
  height: 100vh;
}
/* 右上角天气卡片通用定位 */
.weather-card {
  position: absolute;
  top: 18px;
  right: 18px;
  z-index: 800;
  font-size: 14px;
  overflow: hidden;
  backdrop-filter: blur(10px);
}
/* 展开状态 */
.weather-expanded {
  width: 260px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 3px 12px rgba(0, 0, 0, 0.18);
}
/* 折叠状态：参考第二张图的小卡片 */
.weather-mini {
  width: 230px;
  height: 76px;
  padding: 0;
  border: none;
  border-radius: 14px;
  color: white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.22);
  cursor: pointer;
}
/* 小卡片内部 */
.weather-mini-content {
  position: relative;
  width: 100%;
  height: 100%;
  padding: 12px 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.weather-mini-temp {
  font-size: 28px;
  font-weight: 500;
  line-height: 1;
}

.weather-mini-info {
  font-size: 14px;
  line-height: 1.35;
  margin-top: 1px;
}

.weather-mini-icon {
  margin-left: auto;
  font-size: 24px;
  line-height: 1;
}

.weather-mini-label {
  position: absolute;
  left: 50%;
  bottom: 7px;
  transform: translateX(-50%);
  font-size: 14px;
  letter-spacing: 2px;
}
/* 展开状态头部 */
.weather-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.weather-title {
  font-weight: bold;
  font-size: 16px;
  color: #2c3e50;
}

.weather-collapse-btn {
  border: none;
  background: transparent;
  color: #2f80ed;
  cursor: pointer;
  font-size: 13px;
  padding: 0;
}

.weather-collapse-btn:hover {
  color: #1c63c7;
}
/* 展开状态内容 */
.weather-main {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  margin-bottom: 8px;
}

.weather-icon {
  font-size: 26px;
}

.weather-row {
  color: #555;
  margin-bottom: 6px;
  line-height: 1.5;
}

.weather-advice {
  padding-top: 8px;
  margin-top: 8px;
  border-top: 1px solid #eee;
  color: #666;
  line-height: 1.55;
}

.weather-refresh {
  width: 100%;
  margin-top: 10px;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #2f80ed;
  color: white;
  cursor: pointer;
}

.weather-refresh:hover {
  background: #1c63c7;
}
/* 不同天气的小卡片背景 */
.weather-sunny.weather-mini {
  background: linear-gradient(135deg, rgba(76, 169, 255, 0.88), rgba(167, 220, 255, 0.72));
}

.weather-cloudy.weather-mini {
  background: linear-gradient(135deg, rgba(116, 156, 190, 0.88), rgba(190, 210, 225, 0.72));
}

.weather-rain.weather-mini {
  background: linear-gradient(135deg, rgba(70, 120, 170, 0.92), rgba(150, 185, 210, 0.78));
}

.weather-thunder.weather-mini {
  background: linear-gradient(135deg, rgba(55, 65, 110, 0.94), rgba(115, 120, 165, 0.8));
}

.weather-snow.weather-mini {
  background: linear-gradient(135deg, rgba(130, 180, 215, 0.9), rgba(225, 240, 250, 0.82));
}

.weather-fog.weather-mini {
  background: linear-gradient(135deg, rgba(135, 145, 150, 0.9), rgba(210, 215, 218, 0.78));
}

.weather-default.weather-mini {
  background: linear-gradient(135deg, rgba(76, 169, 255, 0.88), rgba(167, 220, 255, 0.72));
}
/* 右下角可拖动悬浮机器人按钮 */
.assistant-fab {
  position: fixed;
  z-index: 4000;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  border: none;
  background: #2f80ed;
  color: #fff;
  font-size: 30px;
  cursor: grab;
  box-shadow: 0 8px 22px rgba(0, 0, 0, 0.28);
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  touch-action: none;
}
.assistant-fab:active {
  cursor: grabbing;
  transform: scale(0.96);
}

.assistant-fab:hover {
  background: #1c63c7;
}

/* 小助手聊天面板：居中大窗口，占屏幕约三分之二 */
.assistant-panel {
  position: fixed;
  left: 50%;
  top: 50%;
  width: 66vw;
  height: 66vh;
  max-width: 1100px;
  min-width: 760px;
  min-height: 560px;
  transform: translate(-50%, -50%);
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #dce6f2;
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.32);
  z-index: 3600;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 小助手标题栏 */
.assistant-header {
  height: 50px;
  padding: 0 18px;
  background: #2f80ed;
  color: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: bold;
  flex-shrink: 0;
}

.assistant-header button {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: white;
  font-size: 24px;
  cursor: pointer;
  line-height: 1;
}

/* 小助手内容区 */
.assistant-body {
  flex: 1;
  padding: 16px 18px;
  overflow-y: auto;
  background: #f7f9fc;
}

/* 消息行 */
.assistant-message {
  margin-bottom: 14px;
  display: flex;
  flex-direction: column;
}

.assistant-message.user {
  align-items: flex-end;
}

.assistant-message.assistant {
  align-items: flex-start;
}

/* 消息气泡 */
.message-content {
  max-width: 78%;
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.65;
  white-space: pre-wrap;
}

.assistant-message.user .message-content {
  background: #2f80ed;
  color: white;
}

.assistant-message.assistant .message-content {
  background: white;
  color: #333;
  border: 1px solid #e1e6ef;
}

/* 输入区 */
.assistant-input-box {
  padding: 14px 16px;
  border-top: 1px solid #e1e6ef;
  background: white;
  flex-shrink: 0;
}

.assistant-input-box textarea {
  width: 100%;
  height: 78px;
  padding: 10px 12px;
  border: 1px solid #cfd8e6;
  border-radius: 10px;
  resize: vertical;
  outline: none;
  font-size: 14px;
  line-height: 1.5;
  box-sizing: border-box;
}

.assistant-input-box button {
  width: 100%;
  margin-top: 8px;
  padding: 10px;
  border: none;
  border-radius: 10px;
  background: #2f80ed;
  color: white;
  cursor: pointer;
  font-size: 15px;
  font-weight: bold;
}

.assistant-input-box button:hover {
  background: #1c63c7;
}
/**搜索框 */
.top-search-box {
  position: absolute;
  top: 18px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 850;
  display: flex;
  width: 620px;
  height: 42px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.65);
  border-radius: 22px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.location-btn {
  width: 54px;
  border: none;
  background: rgba(47, 128, 237, 0.92);
  color: white;
  cursor: pointer;
  font-size: 17px;
}

.location-btn:hover {
  background: rgba(28, 99, 199, 0.95);
}

.top-search-box input {
  flex: 1;
  border: none;
  padding: 0 18px;
  outline: none;
  font-size: 14px;
  background: transparent;
  color: #333;
}

.top-search-box input::placeholder {
  color: rgba(80, 80, 80, 0.75);
}

.search-btn {
  width: 86px;
  border: none;
  background: rgba(47, 128, 237, 0.92);
  color: white;
  cursor: pointer;
  font-weight: bold;
}

.search-btn:hover {
  background: rgba(28, 99, 199, 0.95);
}

.clear-search-btn {
  width: 72px;
  border: none;
  background: rgba(149, 165, 166, 0.92);
  color: white;
  cursor: pointer;
  font-weight: bold;
}

.clear-search-btn:hover {
  background: rgba(127, 140, 141, 0.96);
}
/**规划按钮 */
.route-plan-box {
  margin-top: 10px;
}
.route-plan-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.5;
}
.route-plan-label {
  flex-shrink: 0;
  font-weight: bold;
  color: #555;
  margin-right: 4px;
}
.route-summary {
  margin-top: 10px;
  padding: 10px;
  background: #f7fbff;
  border: 1px solid #d6eaff;
  border-radius: 6px;
  font-size: 14px;
}
.route-summary p {
  margin: 4px 0;
}
/**在线搜索点位标签 */
:deep(.online-poi-label) {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid #8e44ad;
  color: #5e3370;
  font-size: 12px;
  font-weight: bold;
  padding: 3px 6px;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.24);
}
:deep(.online-poi-label::before) {
  display: none;
}
/**天气开关样式 */
.weather-follow-box {
  margin-top: 8px;
  padding: 8px;
  background: rgba(47, 128, 237, 0.06);
  border: 1px solid rgba(47, 128, 237, 0.18);
  border-radius: 8px;
}

.weather-switch {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
}

.weather-switch input {
  cursor: pointer;
}

.weather-switch input:disabled {
  cursor: not-allowed;
}

.weather-target-text {
  margin-top: 5px;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}
.local-file-name {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}
.sidebar button.active {
  background: #1456a8;
  box-shadow: inset 0 0 0 2px rgba(255, 255, 255, 0.35);
}

.three-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.three-buttons button {
  font-size: 13px;
  padding: 9px 4px;
}
/**客流 */
.crowd-box {
  margin-top: 10px;
}

.crowd-row {
  margin-bottom: 10px;
}

.crowd-label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
  font-weight: bold;
}

.crowd-summary {
  margin-top: 10px;
  padding: 10px;
  background: #f7fbff;
  border: 1px solid #d6eaff;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.5;
}

.crowd-summary p {
  margin: 4px 0;
}

.crowd-legend {
  display: flex;
  gap: 12px;
  margin-top: 10px;
  font-size: 13px;
  color: #555;
}

.legend-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 4px;
}

.legend-dot.comfortable {
  background: #27ae60;
}

.legend-dot.medium {
  background: #f39c12;
}

.legend-dot.crowded {
  background: #e74c3c;
}
/**交通态势 */
.traffic-box {
  margin-top: 10px;
}

.traffic-row {
  margin-bottom: 10px;
}

.traffic-label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
  font-weight: bold;
}

.traffic-summary {
  margin-top: 10px;
  padding: 10px;
  background: #f7fbff;
  border: 1px solid #d6eaff;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.5;
}

.traffic-summary p {
  margin: 4px 0;
}
/**动态路线 */
.dynamic-box {
  margin-top: 10px;
}
.dynamic-row {
  margin-bottom: 10px;
}
.dynamic-label {
  display: block;
  font-size: 14px;
  color: #555;
  margin-bottom: 6px;
  font-weight: bold;
}
.dynamic-result {
  margin-top: 10px;
  padding: 10px;
  background: #fffaf0;
  border: 1px solid #ffe0a3;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.5;
}
.dynamic-result h4 {
  margin: 0 0 8px 0;
}
.dynamic-result p {
  margin: 4px 0;
}
.dynamic-result ul {
  margin: 6px 0 6px 18px;
  padding: 0;
}
/**agent标签 */
.agent-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e5eaf2;
}
.agent-tabs button {
  padding: 6px 12px;
  border: none;
  border-radius: 999px;
  background: #edf2f7;
  color: #333;
  cursor: pointer;
  font-size: 13px;
}
.agent-tabs button.active {
  background: #2f80ed;
  color: white;
}
/**大屏 */
.dashboard-overlay {
  position: fixed;
  inset: 0;
  z-index: 3000;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  justify-content: center;
  align-items: center;
}
.dashboard-panel {
  width: 82vw;
  height: 82vh;
  background: #f7fbff;
  border-radius: 14px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.25);
  padding: 18px;
  box-sizing: border-box;
  overflow: hidden;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}
.dashboard-header h2 {
  margin: 0;
  font-size: 22px;
}
.dashboard-header button {
  width: auto;
  padding: 8px 16px;
  background: #2f80ed;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}
.dashboard-card {
  background: white;
  border-radius: 10px;
  padding: 14px;
  border: 1px solid #dde8f5;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.dashboard-card .card-title {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}
.dashboard-card strong {
  font-size: 28px;
  color: #2f80ed;
}
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  height: calc(100% - 150px);
  overflow-y: auto;
}
.dashboard-chart {
  background: white;
  border-radius: 10px;
  border: 1px solid #dde8f5;
  min-height: 240px;
  padding: 10px;
  box-sizing: border-box;
}
/**langchain测试 */
.langchain-demo-box {
  margin-top: 12px;
  padding: 12px;
  border-top: 1px solid #e0e6ef;
  background: #ffffff;
  border-radius: 10px;
}

.langchain-demo-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  font-weight: bold;
  color: #333;
}

.langchain-demo-title button {
  width: auto;
  padding: 5px 10px;
  font-size: 12px;
  background: #eef4ff;
  color: #2f80ed;
  border: 1px solid #b8d4ff;
  border-radius: 6px;
  cursor: pointer;
}

.langchain-demo-content {
  margin-top: 8px;
}

.langchain-demo-desc {
  margin: 0 0 6px 0;
  font-size: 12px;
  color: #777;
  line-height: 1.4;
}

.langchain-demo-input {
  width: 100%;
  min-height: 64px;
  padding: 9px;
  font-size: 13px;
  border: 1px solid #d7dde8;
  border-radius: 8px;
  resize: vertical;
  box-sizing: border-box;
}

.langchain-demo-btn {
  width: 100%;
  margin-top: 7px;
  padding: 9px;
  background: #2f80ed;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.langchain-demo-btn:disabled {
  background: #9bbce8;
  cursor: not-allowed;
}

.langchain-demo-result {
  margin-top: 8px;
  padding: 9px;
  background: #f7fbff;
  border: 1px solid #d6eaff;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  color: #333;
  white-space: pre-wrap;
}
/**Agent 执行信息区域 */
.agent-execute-meta {
  max-width: 78%;
  margin-top: 7px;
  padding: 9px 11px;
  background: #eef5ff;
  border: 1px solid #d5e7ff;
  border-radius: 10px;
  font-size: 12px;
  color: #3a4a5f;
  line-height: 1.65;
}

.tool-tag {
  display: inline-block;
  margin: 2px 4px 2px 0;
  padding: 2px 7px;
  background: #dcecff;
  color: #2f80ed;
  border-radius: 999px;
  font-size: 12px;
}
/**响应式适配 */
@media (max-width: 900px) {
  .assistant-panel {
    width: 92vw;
    height: 82vh;
    min-width: auto;
    min-height: auto;
  }

  .message-content,
  .agent-execute-meta {
    max-width: 90%;
  }
}
/**手机访问界面设置 */
.mobile-sidebar-header,
.mobile-menu-btn,
.mobile-sidebar-mask {
  display: none;
}
@media (max-width: 768px) {
  .map-page {
    display: block;
    width: 100vw;
    height: 100dvh;
    overflow: hidden;
  }
  .map-wrapper,
  #map {
    width: 100vw;
    height: 100dvh;
  }
  .mobile-menu-btn {
    display: block;
    position: fixed;
    left: 12px;
    top: max(12px, env(safe-area-inset-top));
    z-index: 2100;
    width: auto;
    min-width: 78px;
    height: 38px;
    padding: 0 12px;
    border: none;
    border-radius: 999px;
    background: rgba(47, 128, 237, 0.96);
    color: #fff;
    font-size: 14px;
    font-weight: 700;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.22);
  }
  .mobile-sidebar-mask {
    display: block;
    position: fixed;
    inset: 0;
    z-index: 1990;
    background: rgba(0, 0, 0, 0.38);
  }
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    z-index: 2000;
    width: min(88vw, 360px);
    min-width: 0;
    max-width: 360px;
    height: 100dvh;
    padding: calc(12px + env(safe-area-inset-top)) 12px calc(18px + env(safe-area-inset-bottom));
    border-right: none;
    border-radius: 0 18px 18px 0;
    box-shadow: 8px 0 24px rgba(0, 0, 0, 0.22);
    transform: translateX(-105%);
    transition: transform 0.24s ease;
    -webkit-overflow-scrolling: touch;
  }
  .mobile-sidebar-open .sidebar {
    transform: translateX(0);
  }
  .mobile-sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 2;
    margin: -4px -2px 10px;
    padding: 8px 2px 10px;
    background: #f8f8f8;
    font-weight: 700;
    color: #1f2d3d;
  }
  .mobile-sidebar-header button {
    width: 34px;
    height: 34px;
    margin: 0;
    padding: 0;
    border-radius: 50%;
    background: #eef3fb;
    color: #333;
    font-size: 22px;
    line-height: 1;
  }
  .sidebar h2 {
    font-size: 17px;
    margin-bottom: 6px;
  }
  .sidebar p,
  .panel-box summary,
  .layer-check,
  .detail-row,
  .route-plan-row,
  .traffic-row,
  .crowd-row {
    font-size: 13px;
  }
  .panel-box,
  .info-box,
  .filter-box,
  .search-box,
  .nearby-box,
  .route-box {
    margin-top: 10px;
    padding: 9px;
    border-radius: 10px;
  }
  .button-row {
    gap: 6px;
    margin-top: 8px;
  }
  .button-row button,
  .sidebar button,
  .select-input,
  .search-input,
  .langchain-demo-input,
  .assistant-input-box textarea {
    min-height: 38px;
    font-size: 14px;
  }

  .top-search-box {
    top: calc(58px + env(safe-area-inset-top));
    left: 12px;
    right: 12px;
    transform: none;
    width: auto;
    height: 40px;
    border-radius: 20px;
  }

  .location-btn {
    width: 42px;
    flex-shrink: 0;
  }

  .top-search-box input {
    min-width: 0;
    padding: 0 10px;
    font-size: 14px;
  }

  .search-btn {
    width: 58px;
    flex-shrink: 0;
    font-size: 13px;
  }

  .clear-search-btn {
    width: 46px;
    flex-shrink: 0;
    font-size: 13px;
  }

  .weather-card {
    top: calc(108px + env(safe-area-inset-top));
    right: 12px;
    z-index: 850;
  }

  .weather-expanded {
    width: min(82vw, 260px);
    max-height: 42vh;
    overflow-y: auto;
    padding: 10px;
  }

  .weather-mini {
    width: 168px;
    height: 62px;
  }

  .assistant-fab {
    width: 54px;
    height: 54px;
    font-size: 25px;
  }

  .assistant-panel {
    width: 100vw;
    height: 100dvh;
    min-width: 0;
    min-height: 0;
    max-width: none;
    border-radius: 0;
  }

  .assistant-header {
    height: 46px;
    padding: 0 14px;
  }

  .assistant-body {
    padding: 12px;
  }

  .message-content,
  .agent-execute-meta {
    max-width: 94%;
    font-size: 14px;
  }

  .agent-tabs {
    gap: 6px;
    overflow-x: auto;
    flex-wrap: nowrap;
    padding-bottom: 8px;
  }

  .agent-tabs button {
    flex: 0 0 auto;
    padding: 6px 10px;
    font-size: 12px;
  }

  .assistant-input-box {
    padding: 10px 12px calc(10px + env(safe-area-inset-bottom));
  }

  .assistant-input-box textarea {
    height: 66px;
  }

  .dashboard-overlay {
    align-items: stretch;
  }

  .dashboard-panel {
    width: 100vw;
    height: 100dvh;
    border-radius: 0;
    padding: calc(12px + env(safe-area-inset-top)) 10px calc(12px + env(safe-area-inset-bottom));
    overflow-y: auto;
  }

  .dashboard-header h2 {
    font-size: 17px;
  }

  .dashboard-cards {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }

  .dashboard-card strong {
    font-size: 21px;
  }

  .dashboard-grid {
    grid-template-columns: 1fr;
    height: auto;
    overflow: visible;
  }

  .dashboard-chart {
    min-height: 260px;
  }
}
@media (max-width: 420px) {
  .sidebar {
    width: 92vw;
  }

  .weather-expanded {
    width: calc(100vw - 20px);
  }

  .dashboard-cards {
    grid-template-columns: 1fr;
  }
}
</style>