<template>
  <div class="home">
    <!-- <div class="author-info">
      <p>沈彦廷(Yanting Shen);Tongji University;college of architecture and urban planning;syt4027@tongji.edu.cn&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;朱俊霖(Junlin Zhu);Tongji University;college of architecture and urban planning;2430075@tongji.edu.cn</p>
      <p style="color: #cbcbcb;">上海多源涌现科技有限公司 Shanghai Multi-Source Emergence Technology Co., Ltd.</p>
    </div> -->
    <div class="viewport-container">
      <canvas ref="canvasRef" class="canvas"></canvas>

      <!-- 添加语言切换按钮 -->
      <div class="language-switch">
        <button @click="toggleLanguage" class="language-button">
          {{ currentLanguage === 'zh' ? '中' : 'EN' }}
        </button>
        <VideoButton :currentLanguage="currentLanguage" />
        <button @click="toggleHelpPanel" class="help-button">
          {{ currentLanguage === 'zh' ? '指标解读' : 'Index Guide' }}
        </button>
      </div>

      <div class="controls">
        <button @click="handleBackButton" class="back-button">
          <span class="back-icon">←</span> {{ currentLanguage === 'zh' ? '返回上一步' : 'Back' }}
        </button>
        <div class="button-group">
          <button @click="showIntersectionFaces" class="mode-button" :class="{ 'active': showIntersections }">
            {{ currentLanguage === 'zh' ? '显示外墙面' : 'Show External Wall' }}
          </button>
          <button @click="toggleClippedFaces" class="mode-button" :class="{ 'active': !showIntersections && showClippedFaces }">
            {{ currentLanguage === 'zh' ? '显示内墙面' : 'Show Internal Wall' }}
          </button>
          <button @click="toggleAdjacencyMatrixDialog" class="full-width-button">
            {{ currentLanguage === 'zh' ? '显示邻接矩阵' : 'Show Adjacency Matrix' }}
          </button>
        </div>
      </div>
      <!-- 添加到左侧视口的侧边栏 -->
      <div class="left-sidebar" :class="{ 'collapsed': !isSidebarExpanded }" v-if="currentSelectedGroupIndex !== null && currentSelectedGroupIndex >= 0 && currentSelectedGroupIndex < faceGroups.length">
        <div class="sidebar-toggle" @click="isSidebarExpanded = !isSidebarExpanded">
          <span class="toggle-arrow" :class="{ 'collapsed': !isSidebarExpanded }">{{ isSidebarExpanded ? '›' : '‹' }}</span>
        </div>
        <div class="sidebar-content" v-show="isSidebarExpanded">
          <h3>
            {{ currentLanguage === 'zh' ? '构件属性' : 'Component Properties' }}
          </h3>
          <div class="property-item">
            <span class="property-label"></span>
            <span class="property-value">{{ currentLanguage === 'zh' ? '优化前' : 'Before' }}</span>
            <span class="property-value">{{ currentLanguage === 'zh' ? '优化后' : 'After' }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '序号' : 'No.' }}:</span>
            <span class="property-value">{{ currentSelectedGroupIndex}}</span>
            <span class="property-value">{{ currentSelectedGroupIndex}}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '大类' : 'Type' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].category }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].category }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '外接条件' : 'Out' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].externalCondition }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].externalCondition }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '面积' : 'Area' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].area.toFixed(2) }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].area.toFixed(2) }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '形状系数' : 'SI' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].shapeCoefficient.toFixed(2) }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].shapeCoefficient.toFixed(2) }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '子面类型系数' : 'SType' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].subFaceTypeCoefficient }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].subFaceTypeCoefficient }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '子面总面积' : 'SArea' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].subFaceTotalArea.toFixed(2) }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].subFaceTotalArea.toFixed(2) }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '子面U值' : 'SCon' }}:</span>
            <span class="property-value">
              {{ faceGroups[currentSelectedGroupIndex].subFaceUValue.toFixed(2) }}
            </span>
            <span class="property-value" style="font-weight: bold;">
              {{ currentSelectedGroupIndex !== null && selectedSolution && selectedSolution.nodes[currentSelectedGroupIndex] ? selectedSolution.nodes[currentSelectedGroupIndex].SCon?.toFixed(2) || (currentLanguage === 'zh' ? '无' : 'None') : (currentLanguage === 'zh' ? '无' : 'None') }}
            </span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '子面SHGC' : 'SSHGC' }}:</span>
            <span class="property-value">
              {{ faceGroups[currentSelectedGroupIndex].subFaceSHGC.toFixed(2) }}
            </span>
            <span class="property-value" style="font-weight: bold;">
              {{ currentSelectedGroupIndex !== null && selectedSolution && selectedSolution.nodes[currentSelectedGroupIndex] ? selectedSolution.nodes[currentSelectedGroupIndex].SSHGC?.toFixed(2) || (currentLanguage === 'zh' ? '无' : 'None') : (currentLanguage === 'zh' ? '无' : 'None') }}
            </span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '导热系数' : 'Con' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].conductivity.toFixed(2) }}</span>
            <span class="property-value" style="font-weight: bold;">
              {{ currentSelectedGroupIndex !== null && selectedSolution && selectedSolution.nodes[currentSelectedGroupIndex] ? selectedSolution.nodes[currentSelectedGroupIndex].Con?.toFixed(2) || (currentLanguage === 'zh' ? '无' : 'None') : (currentLanguage === 'zh' ? '无' : 'None') }}
            </span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '厚度' : 'Thi' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].thickness.toFixed(2) }}</span>
            <span class="property-value" style="font-weight: bold;">
              {{ currentSelectedGroupIndex !== null && selectedSolution && selectedSolution.nodes[currentSelectedGroupIndex] ? selectedSolution.nodes[currentSelectedGroupIndex].Thi?.toFixed(2) || (currentLanguage === 'zh' ? '无' : 'None') : (currentLanguage === 'zh' ? '无' : 'None') }}
            </span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '长波辐射吸收比' : 'TA' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].longwaveAbsorptance.toFixed(2) }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].longwaveAbsorptance.toFixed(2) }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '太阳辐射吸收比' : 'SA' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].solarAbsorptance.toFixed(2) }}</span>
            <span class="property-value" style="font-weight: bold;">
              {{ currentSelectedGroupIndex !== null && selectedSolution && selectedSolution.nodes[currentSelectedGroupIndex] ? selectedSolution.nodes[currentSelectedGroupIndex].SA?.toFixed(2) || (currentLanguage === 'zh' ? '无' : 'None') : (currentLanguage === 'zh' ? '无' : 'None') }}
            </span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '可见光辐射吸收比' : 'VA' }}:</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].visibleAbsorptance.toFixed(2) }}</span>
            <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].visibleAbsorptance.toFixed(2) }}</span>
          </div>
          <div class="property-item">
            <span class="property-label">{{ currentLanguage === 'zh' ? '朝向' : 'Dir' }}:</span>
            <span class="property-value">{{ currentLanguage === 'zh' ? faceGroups[currentSelectedGroupIndex].direction : faceGroups[currentSelectedGroupIndex].direction.replace('东', 'East').replace('南', 'South').replace('西', 'West').replace('北', 'North').replace('下', 'Down').replace('上', 'Up') }}</span>
            <span class="property-value">{{ currentLanguage === 'zh' ? faceGroups[currentSelectedGroupIndex].direction : faceGroups[currentSelectedGroupIndex].direction.replace('东', 'East').replace('南', 'South').replace('西', 'West').replace('北', 'North').replace('下', 'Down').replace('上', 'Up') }}</span>
          </div>
        </div>
      </div>


      <div class="notch-container">
        <div class="notch">
          <span class="notch-text">
            {{ currentLanguage === 'zh' ? '第三步：模型优化' : 'Step 3: Model Optimization' }}
          </span>
        </div>
      </div>
    </div>
    <div class="right-container">
      <div class="right-panel upper-panel">
        <!-- 添加刘海屏标签 -->
        <div class="notch-container">
          <div class="notch" :class="{ 'selected': selectedNotch === 'optimization' }" @click="selectedNotch = 'optimization'">
            <span class="notch-text">
              {{ currentLanguage === 'zh' ? '模型优化' : 'Model Optimization' }}
            </span>
          </div>
          <div class="notch" :class="{ 'selected': selectedNotch === 'comparison' }" @click="selectedNotch = 'comparison'">
            <span class="notch-text">
              {{ currentLanguage === 'zh' ? '结果对比' : 'Result Comparison' }}
            </span>
          </div>
          <div class="notch" :class="{ 'selected': selectedNotch === 'export' }" @click="selectedNotch = 'export'">
            <span class="notch-text">
              {{ currentLanguage === 'zh' ? '导出表格' : 'Export Table' }}
            </span>
          </div>

        </div>
        <div class="panel-content">
          <div v-if="apiResponse" class="api-response">
            <!-- 主容器 -->
            <div class="main-content-container">
              <!-- 左侧容器 -->
              <div class="left-container">
                <!-- 预测值显示 -->
                <div class="result-section prediction-section">
                  <h3 style="font-size: 12px;font-weight: bold;">
                    {{ currentLanguage === 'zh' ? '预测能耗' : 'Energy Consumption' }}
                  </h3>
                  <div class="prediction-value">{{ apiResponse.prediction ? apiResponse.prediction.toFixed(2) : '未知' }} kWh</div>
                </div>

                <!-- 优化参数设置 -->
                <div class="result-section optimization-params-section">
                  <h3 style="font-size: 12px;font-weight: bold;text-align: center;">
                    {{ currentLanguage === 'zh' ? '优化参数' : 'Optimization Parameters' }}
                  </h3>
                  <div class="param-item">
                    <label>{{ currentLanguage === 'zh' ? '种群大小' : 'Population Size' }}:</label>
                    <input type="number" v-model="optimizationParams.populationSize" min="10" max="200" step="1" />
                  </div>
                  <div class="param-item">
                    <label>{{ currentLanguage === 'zh' ? '迭代次数' : 'Iterations' }}:</label>
                    <input type="number" v-model="optimizationParams.iterations" min="10" max="1000" step="1" />
                  </div>
                  <div class="param-item">
                    <label>{{ currentLanguage === 'zh' ? '墙体材料' : 'Wall Material' }}:</label>
                    <div class="select-wrapper">
                      <div class="select-display">
                        {{ wallMaterials[optimizationParams.wallMaterial] ? (currentLanguage === 'zh' ? wallMaterials[optimizationParams.wallMaterial].Material?.substring(0, 3) + '...' : wallMaterials[optimizationParams.wallMaterial].MaterialEN?.substring(0, 3) + '...') : (currentLanguage === 'zh' ? '选择材料' : 'Select Material') }}
                      </div>
                      <select v-model="optimizationParams.wallMaterial" class="hidden-select">
                        <option
                          v-for="(material, index) in wallMaterials"
                          :key="index"
                          :value="index"
                        >
                          {{ currentLanguage === 'zh' ? material.Material : material.MaterialEN }}
                        </option>
                      </select>
                    </div>
                  </div>
                  <button @click="startOptimization" class="optimization-button" :disabled="isLoading">
                    <span v-if="isLoading" class="loading-spinner"></span>
                    <span v-else>{{ currentLanguage === 'zh' ? '开始优化' : 'Start Optimization' }}</span>
                  </button>
                </div>
              </div>

              <!-- 平面坐标容器 -->
              <div class="coordinate-container">
                <svg class="coordinate-system" viewBox="0 0 400 300" preserveAspectRatio="none">
                  <!-- X轴 -->
                  <line x1="25" y1="250" x2="350" y2="250" stroke="#333" stroke-width="1"/>
                  <!-- Y轴 -->
                  <line x1="25" y1="250" x2="25" y2="50" stroke="#333" stroke-width="1"/>
                  <!-- X轴箭头 -->
                  <polygon points="350,250 340,245 340,255" fill="#333"/>
                  <!-- Y轴箭头 -->
                  <polygon points="25,50 20,60 30,60" fill="#333"/>
                  <!-- X轴标签 -->
                  <text x="360" y="255" font-size="12" fill="#333">{{ currentLanguage === 'zh' ? '价格' : 'Cost' }}</text>
                  <!-- Y轴标签 -->
                  <text x="20" y="45" font-size="12" fill="#333">{{ currentLanguage === 'zh' ? '能耗' : 'Energy' }}</text>
                  <!-- 原点标签 -->
                  <text x="35" y="265" font-size="10" fill="#666">0</text>

                  <!-- 绘制悬停辅助线 -->
                  <g v-if="hoveredSolution">
                    <!-- 到X轴的垂直线 -->
                    <line
                      :x1="getScaledX(hoveredSolution.cost)"
                      :y1="getScaledY(hoveredSolution.energy)"
                      :x2="getScaledX(hoveredSolution.cost)"
                      y2="250"
                      stroke="#999"
                      stroke-width="1"
                      stroke-dasharray="3,3"
                    />
                    <!-- 到Y轴的水平线 -->
                    <line
                      x1="25"
                      :y1="getScaledY(hoveredSolution.energy)"
                      :x2="getScaledX(hoveredSolution.cost)"
                      :y2="getScaledY(hoveredSolution.energy)"
                      stroke="#999"
                      stroke-width="1"
                      stroke-dasharray="3,3"
                    />
                  </g>

                  <!-- 绘制优化方案数据点 -->
                  <circle
                    v-for="(solution, index) in paretoSolutions"
                    :key="'solution-' + index"
                    :cx="getScaledX(solution.cost)"
                    :cy="getScaledY(solution.energy)"
                    r="7"
                    :fill="selectedSolution && selectedSolution.cost === solution.cost && selectedSolution.energy === solution.energy ? '#FF0000' : '#4CAF50'"
                    stroke="#F2F2F2"
                    stroke-width="1"
                    @mouseenter="hoveredSolution = {cost: solution.cost, energy: solution.energy, index: index}"
                    @mouseleave="hoveredSolution = null"
                    @click="selectSolution(solution, index)"
                    style="cursor: pointer;"
                  />

                  <!-- 悬停信息显示 -->
                  <g v-if="hoveredSolution">
                    <rect
                      :x="getScaledX(hoveredSolution.cost) + 10"
                      :y="getScaledY(hoveredSolution.energy) - 25"
                      width="120"
                      height="45"
                      fill="rgba(0,0,0,0.8)"
                      stroke="#333"
                      rx="3"
                    />
                    <text
                      :x="getScaledX(hoveredSolution.cost) + 15"
                      :y="getScaledY(hoveredSolution.energy) - 10"
                      font-size="10"
                      fill="white"
                    >
                      {{ currentLanguage === 'zh' ? '方案' : 'Solution' }}: {{ hoveredSolution.index }}
                    </text>
                    <text
                      :x="getScaledX(hoveredSolution.cost) + 15"
                      :y="getScaledY(hoveredSolution.energy) + 2"
                      font-size="10"
                      fill="white"
                    >
                      {{ currentLanguage === 'zh' ? '价格' : 'Cost' }}: {{ hoveredSolution.cost.toFixed(2) }}
                    </text>
                    <text
                      :x="getScaledX(hoveredSolution.cost) + 15"
                      :y="getScaledY(hoveredSolution.energy) + 14"
                      font-size="10"
                      fill="white"
                    >
                      {{ currentLanguage === 'zh' ? '能耗' : 'Energy' }}: {{ hoveredSolution.energy.toFixed(2) }}
                    </text>
                  </g>
                </svg>
              </div>
            </div>

            <!-- 方案详情表格容器 -->
            <div v-if="selectedSolution && selectedNotch === 'optimization'" class="solution-details-container">
              <h3>{{ currentLanguage === 'zh' ? `方案${selectedSolutionIndex}      能耗：${selectedSolution.energy.toFixed(2)}kWh      总价：${selectedSolution.cost.toFixed(2)}元` : `Solution ${selectedSolutionIndex}      Energy: ${selectedSolution.energy.toFixed(2)}kWh      Cost: ${selectedSolution.cost.toFixed(2)}` }}</h3>
              <div class="table-container">
                <table class="materials-table">
                  <thead>
                    <tr>
                      <th>{{ currentLanguage === 'zh' ? '节点' : 'Node' }}</th>
                      <th>{{ currentLanguage === 'zh' ? '墙体材料' : 'Wall Material' }}</th>
                      <th>{{ currentLanguage === 'zh' ? '保温层材料' : 'Insulation Material' }}</th>
                      <th>{{ currentLanguage === 'zh' ? '面层材料' : 'Finish Material' }}</th>
                      <th>{{ currentLanguage === 'zh' ? '窗户玻璃材料' : 'Window Glass Material' }}</th>
                      <th>{{ currentLanguage === 'zh' ? '窗框材料' : 'Window Frame Material' }}</th>
                      <th>{{ currentLanguage === 'zh' ? '门材料' : 'Door Material' }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(node, index) in selectedSolution.nodes" :key="'node-' + index"
                        @click="highlightGroup(index)"
                        :class="{ 'selected-row': currentSelectedGroupIndex === index }"
                        style="cursor: pointer;">
                      <td>{{ index }}</td>
                      <td>{{currentLanguage === 'zh' ? node.WMat : node.WMatEN || 'None' }}</td>
                      <td>{{ currentLanguage === 'zh' ? node.PMat : node.PMatEN || 'None' }}</td>
                      <td>{{ currentLanguage === 'zh' ? node.FMat : node.FMatEN || 'None' }}</td>
                      <td>{{ currentLanguage === 'zh' ? node.WGMat : node.WGMatEN || 'None' }}</td>
                      <td>{{ currentLanguage === 'zh' ? node.WFMat : node.WFMatEN || 'None' }}</td>
                      <td>{{ currentLanguage === 'zh' ? node.DMat : node.DMatEN || 'None' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 方案对比容器 -->
            <div v-if="selectedNotch === 'comparison'" class="comparison-container">
              <div class="comparison-left">
                <div class="comparison-controls">
                  <div class="control-item">
                    <label>{{ currentLanguage === 'zh' ? '方案' : 'Solution' }}:</label>
                    <select v-model="comparisonLeftSolution" class="comparison-select">
                      <option v-for="(solution, index) in paretoSolutions" :key="'left-' + index" :value="index">
                        {{ currentLanguage === 'zh' ? `方案${index}` : `Solution ${index}` }}
                      </option>
                    </select>
                  </div>
                  <div class="control-item">
                    <label>{{ currentLanguage === 'zh' ? '节点' : 'Node' }}:</label>
                    <select v-model="comparisonSelectedNode" class="comparison-select">
                      <option v-for="(group, index) in faceGroups" :key="'node-' + index" :value="index">
                        {{ currentLanguage === 'zh' ? `节点${index}` : `Node ${index}` }}
                      </option>
                    </select>
                  </div>
                </div>
                <div v-if="paretoSolutions[comparisonLeftSolution]" class="solution-summary">
                  <div class="summary-item">
                    <span class="summary-label">{{ currentLanguage === 'zh' ? '能耗' : 'Energy' }}:</span>
                    <span class="summary-value">{{ paretoSolutions[comparisonLeftSolution].energy?.toFixed(2) || 'N/A' }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">{{ currentLanguage === 'zh' ? '价格' : 'Cost' }}:</span>
                    <span class="summary-value">{{ paretoSolutions[comparisonLeftSolution].cost?.toFixed(2) || 'N/A' }}</span>
                  </div>
                </div>
                <div v-if="paretoSolutions[comparisonLeftSolution] && paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode]" class="material-info">
                  <div class="material-row">{{ currentLanguage === 'zh' ? '墙体材料' : 'Wall Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].WMat : paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].WMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '保温层材料' : 'Insulation Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].PMat : paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].PMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '面层材料' : 'Finish Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].FMat : paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].FMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '窗户玻璃材料' : 'Window Glass Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].WGMat : paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].WGMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '窗框材料' : 'Window Frame Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].WFMat : paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].WFMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '门材料' : 'Door Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].DMat : paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].DMatEN || 'None' }}</div>
                </div>
                <div v-if="paretoSolutions[comparisonLeftSolution] && paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode] && faceGroups[comparisonSelectedNode]" class="comparison-chart">
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '导热系数' : 'Con' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].conductivity, 'Con') }">
                        {{ faceGroups[comparisonSelectedNode].conductivity.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].Con, 'Con'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].conductivity, paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].Con) }">
                        {{ paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].Con?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '厚度' : 'Thi' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].thickness, 'Thi') }">
                        {{ faceGroups[comparisonSelectedNode].thickness.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].Thi, 'Thi'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].thickness, paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].Thi) }">
                        {{ paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].Thi?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '太阳辐射吸收' : 'SA' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].solarAbsorptance, 'SA') }">
                        {{ faceGroups[comparisonSelectedNode].solarAbsorptance.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SA, 'SA'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].solarAbsorptance, paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SA) }">
                        {{ paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SA?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '子面U值' : 'SCon' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].subFaceUValue, 'SCon') }">
                        {{ faceGroups[comparisonSelectedNode].subFaceUValue.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SCon, 'SCon'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].subFaceUValue, paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SCon) }">
                        {{ paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SCon?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '子面SHGC' : 'SSHGC' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].subFaceSHGC, 'SSHGC') }">
                        {{ faceGroups[comparisonSelectedNode].subFaceSHGC.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SSHGC, 'SSHGC'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].subFaceSHGC, paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SSHGC) }">
                        {{ paretoSolutions[comparisonLeftSolution].nodes[comparisonSelectedNode].SSHGC?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                </div>
                <div class="chart-legend">
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #87CEEB;"></span>
                    <span class="legend-text">{{ currentLanguage === 'zh' ? '原值' : 'Original Value' }}</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #4CAF50;"></span>
                    <span class="legend-text">{{ currentLanguage === 'zh' ? '低' : 'Lower' }}</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #F44336;"></span>
                    <span class="legend-text">{{ currentLanguage === 'zh' ? '高' : 'Higher' }}</span>
                  </div>
                </div>
              </div>
              <div class="comparison-right">
                <div class="comparison-controls">
                  <div class="control-item">
                    <label>{{ currentLanguage === 'zh' ? '方案' : 'Solution' }}:</label>
                    <select v-model="comparisonRightSolution" class="comparison-select">
                      <option v-for="(solution, index) in paretoSolutions" :key="'right-' + index" :value="index">
                        {{ currentLanguage === 'zh' ? `方案${index}` : `Solution ${index}` }}
                      </option>
                    </select>
                  </div>
                  <div class="control-item">
                    <label>{{ currentLanguage === 'zh' ? '节点' : 'Node' }}:</label>
                    <select v-model="comparisonSelectedNode" class="comparison-select">
                      <option v-for="(group, index) in faceGroups" :key="'node-' + index" :value="index">
                        {{ currentLanguage === 'zh' ? `节点${index}` : `Node ${index}` }}
                      </option>
                    </select>
                  </div>
                </div>
                <div v-if="paretoSolutions[comparisonRightSolution]" class="solution-summary">
                  <div class="summary-item">
                    <span class="summary-label">{{ currentLanguage === 'zh' ? '能耗' : 'Energy' }}:</span>
                    <span class="summary-value">{{ paretoSolutions[comparisonRightSolution].energy?.toFixed(2) || 'N/A' }}</span>
                  </div>
                  <div class="summary-item">
                    <span class="summary-label">{{ currentLanguage === 'zh' ? '价格' : 'Cost' }}:</span>
                    <span class="summary-value">{{ paretoSolutions[comparisonRightSolution].cost?.toFixed(2) || 'N/A' }}</span>
                  </div>
                </div>
                <div v-if="paretoSolutions[comparisonRightSolution] && paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode]" class="material-info">
                  <div class="material-row">{{ currentLanguage === 'zh' ? '墙体材料' : 'Wall Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].WMat : paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].WMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '保温层材料' : 'Insulation Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].PMat : paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].PMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '面层材料' : 'Finish Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].FMat : paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].FMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '窗户玻璃材料' : 'Window Glass Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].WGMat : paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].WGMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '窗框材料' : 'Window Frame Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].WFMat : paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].WFMatEN || 'None' }}</div>
                  <div class="material-row">{{ currentLanguage === 'zh' ? '门材料' : 'Door Material' }}: {{ currentLanguage === 'zh' ? paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].DMat : paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].DMatEN || 'None' }}</div>
                </div>
                <div v-if="paretoSolutions[comparisonRightSolution] && paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode] && faceGroups[comparisonSelectedNode]" class="comparison-chart">
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '导热系数' : 'Con' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].conductivity, 'Con') }">
                        {{ faceGroups[comparisonSelectedNode].conductivity.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].Con, 'Con'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].conductivity, paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].Con) }">
                        {{ paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].Con?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '厚度' : 'Thi' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].thickness, 'Thi') }">
                        {{ faceGroups[comparisonSelectedNode].thickness.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].Thi, 'Thi'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].thickness, paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].Thi) }">
                        {{ paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].Thi?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '太阳辐射吸收' : 'SA' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].solarAbsorptance, 'SA') }">
                        {{ faceGroups[comparisonSelectedNode].solarAbsorptance.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SA, 'SA'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].solarAbsorptance, paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SA) }">
                        {{ paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SA?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '子面U值' : 'SCon' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].subFaceUValue, 'SCon') }">
                        {{ faceGroups[comparisonSelectedNode].subFaceUValue.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SCon, 'SCon'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].subFaceUValue, paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SCon) }">
                        {{ paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SCon?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                  <div class="chart-item">
                    <div class="chart-label">{{ currentLanguage === 'zh' ? '子面SHGC' : 'SSHGC' }}</div>
                    <div class="chart-bars">
                      <div class="bar-before" :style="{ height: getComparisonBarWidth(faceGroups[comparisonSelectedNode].subFaceSHGC, 'SSHGC') }">
                        {{ faceGroups[comparisonSelectedNode].subFaceSHGC.toFixed(2) }}
                      </div>
                      <div class="bar-after" :style="{ height: getComparisonBarWidth(paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SSHGC, 'SSHGC'), backgroundColor: getComparisonBarColor(faceGroups[comparisonSelectedNode].subFaceSHGC, paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SSHGC) }">
                        {{ paretoSolutions[comparisonRightSolution].nodes[comparisonSelectedNode].SSHGC?.toFixed(2) || 'N/A' }}
                      </div>
                    </div>
                  </div>
                </div>
                <div class="chart-legend">
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #87CEEB;"></span>
                    <span class="legend-text">{{ currentLanguage === 'zh' ? '原值' : 'Original Value' }}</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #4CAF50;"></span>
                    <span class="legend-text">{{ currentLanguage === 'zh' ? '低' : 'Lower' }}</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color" style="background-color: #F44336;"></span>
                    <span class="legend-text">{{ currentLanguage === 'zh' ? '高' : 'Higher' }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 导出表格容器 -->
            <div v-if="selectedNotch === 'export'" class="export-container">
              <!-- 四个基础导出按钮区域 -->
              <div class="basic-export-buttons">
                <button class="export-button basic-export-btn" @click="exportAdjacencyMatrixToCSV">
                  {{ currentLanguage === 'zh' ? '导出邻接矩阵' : 'Export Adjacency Matrix' }}
                </button>
                <button class="export-button basic-export-btn" @click="exportNodeDataToCSV">
                  {{ currentLanguage === 'zh' ? '导出原始节点' : 'Export original node data' }}
                </button>
                <button class="export-button basic-export-btn" @click="exportNodeImportanceToCSV">
                  {{ currentLanguage === 'zh' ? '导出节点重要性' : 'Export Node Importance' }}
                </button>
                <button class="export-button basic-export-btn" @click="exportEdgeImportanceToCSV">
                  {{ currentLanguage === 'zh' ? '导出链接重要性' : 'Export Edge Importance' }}
                </button>
              </div>

              <!-- 导出优化方案区域 -->
              <div class="solution-export-section">
                <div class="solution-select-label">
                  {{ currentLanguage === 'zh' ? '选择要导出的优化方案：' : 'Select solutions to export:' }}
                </div>

                <!-- 方案下拉选择 -->
                <div class="solution-selector">
                  <select
                    v-model="solutionToAdd"
                    class="solution-select"
                    @change="addSolutionTag"
                  >
                    <option value="" disabled>
                      {{ currentLanguage === 'zh' ? '-- 选择方案 --' : '-- Select Solution --' }}
                    </option>
                    <option
                      v-for="(solution, index) in paretoSolutions"
                      :key="'select-solution-' + index"
                      :value="index"
                      :disabled="selectedSolutionsForExport.includes(index)"
                    >
                      {{ currentLanguage === 'zh' ? '方案' : 'Solution' }} {{ index }}
                    </option>
                  </select>
                </div>

                <!-- 已选方案标签显示 -->
                <div class="selected-solutions-tags">
                  <div
                    v-for="solutionIndex in selectedSolutionsForExport"
                    :key="'tag-' + solutionIndex"
                    class="solution-tag"
                  >
                    <span class="tag-text">
                      {{ currentLanguage === 'zh' ? '方案' : 'Solution' }} {{ solutionIndex }}
                    </span>
                    <span class="tag-remove" @click="removeSolutionTag(solutionIndex)">×</span>
                  </div>
                </div>

                <!-- 导出按钮 -->
                <button
                  class="export-button export-solutions-btn"
                  @click="exportSelectedSolutions"
                  :disabled="selectedSolutionsForExport.length === 0"
                >
                  {{ currentLanguage === 'zh' ? '导出优化方案' : 'Export Solutions' }}
                  <span v-if="selectedSolutionsForExport.length > 0">
                    ({{ selectedSolutionsForExport.length }})
                  </span>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            暂无API返回数据
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 邻接矩阵弹窗 -->
  <div v-if="showAdjacencyMatrixDialog" class="matrix-dialog-overlay" @click.self="closeAdjacencyMatrixDialog">
    <div class="matrix-dialog">
      <div class="matrix-dialog-header">
        <h3>{{ currentLanguage === 'zh' ? '构件邻接矩阵' : 'Adjacency Matrix of Components' }}</h3>
        <button class="close-button" @click="closeAdjacencyMatrixDialog">×</button>
      </div>
      <div class="matrix-dialog-content">
        <div class="matrix-description">
          <p>{{ currentLanguage === 'zh' ? '邻接矩阵表示构件之间的连接关系：1表示连接，0表示不连接' : 'The adjacency matrix represents the connection relationship between components: 1 represents a connection, 0 represents no connection' }}</p>
        </div>
        <div class="matrix-table-container">
          <table class="adjacency-matrix">
            <thead>
              <tr>
                <th class="index-cell"></th>
                <th class="index-cell" v-for="(_, colIndex) in adjacencyMatrix" :key="'col-' + colIndex">{{ colIndex + 1 }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, rowIndex) in adjacencyMatrix" :key="'row-' + rowIndex">
                <th class="index-cell">{{ rowIndex + 1 }}</th>
                <td v-for="(cell, colIndex) in row" :key="'cell-' + rowIndex + '-' + colIndex"
                    :class="{ 'connected': cell === 1 && rowIndex !== colIndex, 'self': rowIndex === colIndex }">
                  {{ cell }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- 帮助面板 -->
  <div v-if="showHelpPanel" class="help-panel-overlay" @click.self="toggleHelpPanel">
    <div class="help-panel">
      <div class="help-panel-header">
        <h3>{{ currentLanguage === 'zh' ? '属性解释' : 'Property Explanations' }}</h3>
        <button class="close-button" @click="toggleHelpPanel">×</button>
      </div>
      <div class="help-panel-content">
        <div class="property-explanation">
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'Area / 面积' : 'Area / Area' }}</strong>：{{ currentLanguage === 'zh' ? '该构件的面积大小(m²)' : 'Surface area of the component (Unit: m²)' }}</span>
          </div>
          <div class="property-item">
              <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'SI / 形状系数' : 'SI / Shape Index' }}</strong>：{{ currentLanguage === 'zh' ? '构件的几何规整程度，SI=(周长*周长)/(4*π*Area)' : 'Geometric regularity index, SI = (Perimeter²)/(4π·Area)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'Dir / 朝向' : 'Dir / Orientation' }}</strong>：{{ currentLanguage === 'zh' ? '构件的朝向，0-4分别代表：无（上/下/内墙）、东、南、西、北' : 'Cardinal direction (0-4: None [top/bottom/internal], East, South, West, North)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'Type / 大类' : 'Type / Type' }}</strong>：{{ currentLanguage === 'zh' ? '该构件所属的分类，0-3分别代表：外墙、内墙、地表、屋顶' : 'Component classification (0-3: Exterior wall, Interior wall, Ground, Roof)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'Con / 导热系数' : 'Con / Thermal Conductivity' }}</strong>：{{ currentLanguage === 'zh' ? '构件的热导率（单位：W/m·K）' : 'The thermal conductivity of the material. (Unit: W/(m·K))' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'Thi / 厚度' : 'Thi / Thickness' }}</strong>：{{ currentLanguage === 'zh' ? '构件的厚度（单位：m）' : 'The thickness of the material layer (Unit: m)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'TA / 长波辐射吸收比' : 'TA / Therm Absorptance' }}</strong>：{{ currentLanguage === 'zh' ? '构件吸收的电磁波中，长波辐射比例' : 'The fraction of incident long wave length radiation that is absorbed by the material.' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'SA / 太阳辐射吸收比' : 'SA / Solar Absorptance' }}</strong>：{{ currentLanguage === 'zh' ? '构件吸收的电磁波中，太阳辐射比例' : 'The fraction of incident solar radiation absorbed by the material.' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'VA / 可见光辐射吸收比' : 'VA / Visible Absorptance' }}</strong>：{{ currentLanguage === 'zh' ? '构件吸收的电磁波中，可见光波长辐射比例' : 'The fraction of incident visible wave length radiation absorbed by the material.' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'Out / 外接条件' : 'Out / External Boundary' }}</strong>：{{ currentLanguage === 'zh' ? '该构件所接触的环境，0-2分别代表：室外、墙面、土壤' : 'Contact medium (0-2: Outdoor, Surface, Ground)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'SType / 子面类型' : 'SType / Subface Type' }}</strong>：{{ currentLanguage === 'zh' ? '该构件上拥有的子面类型，0-3分别代表：无、仅窗、仅门、门&窗' : 'Opening configuration (0-3: None, Window only, Door only, Window+Door)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'SArea / 子面总面积' : 'SArea / Opening Area' }}</strong>：{{ currentLanguage === 'zh' ? '该构件所有子面的总面积(m²)' : 'Total fenestration area (Unit: m²)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'SCon / 子面U值' : 'SCon / Subface U-value' }}</strong>：{{ currentLanguage === 'zh' ? '子面的加权导热系数，如果是透明材料则使用u值' : 'TheU-factor of the glazing system including standard air gap resistances on either side of the glazing system.(W/m2*K)' }}</span>
          </div>
          <div class="property-item">
            <span class="property-name"><strong style="font-weight: 900;">{{ currentLanguage === 'zh' ? 'SSHGC / 子面SHGC' : 'SSHGC / Subface SHGC' }}</strong>：{{ currentLanguage === 'zh' ? '子面的加权太阳得热系数' : 'The solar heat gain coefficient of the glazing system.' }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, nextTick, reactive, watch, computed } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import VideoButton from '../components/VideoButton.vue';
import { useRouter, useRoute } from 'vue-router';
import * as XLSX from 'xlsx';
import {
  CubeData,
  cubesToFaces,
  renderFacesInScene,
  Face,
  findAllFaceIntersections,
  computeAllClippedFaces,
  groupConnectedClippedFaces
} from '../utils/cubeToInterval';
import { saveAs } from 'file-saver';

// 获取路由器实例和当前路由
const router = useRouter();
const route = useRoute();

// API返回结果
const apiResponse = ref<any>(null);

// 场景相关变量
const canvasRef = ref<HTMLCanvasElement | null>(null);
const upperCanvasRef = ref<HTMLCanvasElement | null>(null);
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let orbitControls: OrbitControls;
let raycaster: THREE.Raycaster;
let mouse: THREE.Vector2;

// 右上视口场景相关变量
let upperScene: THREE.Scene;
let upperCamera: THREE.PerspectiveCamera;
let upperRenderer: THREE.WebGLRenderer;
let upperOrbitControls: OrbitControls;

// 选中的面
let selectedFace: THREE.Mesh | null = null;
// 原始颜色（用于恢复）
const originalColors = new Map<THREE.Mesh, number>();
// 选中颜色
const SELECTED_COLOR = 0xffffff; // 白色
// 边框对象
let selectionBorder: THREE.LineSegments | null = null;
// 同组面的边框对象数组
let groupSelectionBorders: THREE.LineSegments[] = [];

// 显示模式
const showIntersections = ref(false);
const showClippedFaces = ref(true); // 默认显示裁剪面
// 存储所有面和交集面
let allCubeFaces: Face[] = [];
let intersectionFaces: Face[] = [];
let clippedFaces: Face[] = [];
// 存储场景中的面对象
let cubeFaceMeshes: THREE.Mesh[] = [];
let intersectionFaceMeshes: THREE.Mesh[] = [];
let clippedFaceMeshes: THREE.Mesh[] = [];
// 存储裁剪面的分组信息
let clippedFaceGroups: number[][] = [];

// 选中面的信息
interface FaceInfo {
  index: number;
  direction: string;
  normal: string;
  vertexCount: number;
  cubeIndex: number;
  area: number;
  isIntersection?: boolean;
  parentFaces?: {
    index: number;
    cubeIndex: number;
    direction: string;
  }[];
  childIntersections?: {
    index: number;
    area: number;
    vertexCount: number;
  }[];
  isClipped?: boolean;
  parentFace?: {
    index: number;
    cubeIndex: number;
    direction: string;
  };
}

// 面组类（交集面和裁剪面组）
interface FaceGroup {
  index: number;        // 序号
  type: string;         // 类型：'交集面' 或 '裁剪面组'
  direction: string;    // 朝向
  area: number;         // 面积
  perimeter: number;    // 周长
  shapeCoefficient: number; // 形状系数
  subFaceTypeCoefficient: number; // 子面类型系数：0(无门窗)/1(只有窗)/2(只有门)/3(窗+门)
  subFaceTotalArea: number; // 子面总面积：所有门窗面积之和
  subFaceUValue: number; // 子面U值：传热系数，有子面(门窗)时为1.5，无子面时为0
  subFaceSHGC: number; // 子面SHGC：太阳得热系数，有子面时为0.5，无子面时为0
  conductivity: number; // 导热系数：墙体的导热性能，默认为1，范围0.1-2
  thickness: number;    // 厚度：墙体厚度，默认为0.2，范围0.1-0.5
  longwaveAbsorptance: number; // 长波辐射吸收比：默认为0.9，范围0-1
  solarAbsorptance: number; // 太阳辐射吸收比：默认为0.7，范围0-1
  visibleAbsorptance: number; // 可见光辐射吸收比：默认为0.7，范围0-1
  vertexCount: number;  // 顶点数
  vertices: THREE.Vector3[]; // 顶点列表
  faceIndices: number[]; // 包含的面索引
  windows: { // 添加windows属性存储关联的门窗
    position: THREE.Vector3; // 绝对位置
    width: number;
    height: number;
    type: string; // 类型：'door'或'window'
    uValue: number; // 添加U值属性
    shgc: number; // 添加SHGC值属性
    mesh: THREE.Mesh | null; // 可能为null，因为在切换面组时mesh会被销毁
  }[];
  category: string;     // 添加"大类"属性
  regionClass?: number; // 添加"区域类"属性，默认值为0
  externalCondition: string; // 添加"外接条件"属性
}

const selectedFaceInfo = ref<FaceInfo | null>(null);
const faceGroups = ref<FaceGroup[]>([]);
const adjacencyMatrix = ref<number[][]>([]);
const showAdjacencyMatrix = ref(false);

// 邻接矩阵弹窗状态
const showAdjacencyMatrixDialog = ref(false);

// 方向映射
const directionMap = {
  'x-1': '北',
  'x+1': '南',
  'y-1': '下',
  'y+1': '上',
  'z-1': '东',
  'z+1': '西'
};

// 添加语言相关的响应式变量
const currentLanguage = ref('en'); // 默认英文

// 墙体材料数据
const wallMaterials = ref<{Material: string, MaterialEN: string, Con: number, Price: number}[]>([]);

// 优化参数
const optimizationParams = ref({
  populationSize: 30,
  iterations: 10,
  wallMaterial: 0 // 改为序号，从0开始
});

// Pareto优化方案数据
const paretoSolutions = ref<{cost: number, energy: number, nodes: any[]}[]>([]);

// 加载状态
const isLoading = ref(false);

// 悬停状态
const hoveredSolution = ref<{cost: number, energy: number, index: number} | null>(null);

// 选中的方案
const selectedSolution = ref<{cost: number, energy: number, nodes: any[]} | null>(null);
const selectedSolutionIndex = ref<number>(0);

// 添加帮助面板状态
const showHelpPanel = ref(false);

// 添加刘海标签选中状态
const selectedNotch = ref('optimization'); // 'optimization' 或 'comparison'

// 添加对比容器的选择状态
const comparisonLeftSolution = ref<number>(0); // 左侧选中的方案索引
const comparisonRightSolution = ref<number>(0); // 右侧选中的方案索引
const comparisonSelectedNode = ref<number>(0); // 选中的节点索引（两侧同步）

// 导出优化方案相关
const selectedSolutionsForExport = ref<number[]>([]); // 已选中要导出的方案索引数组
const solutionToAdd = ref<string>(''); // 下拉菜单当前选中的方案

// 添加方案标签
const addSolutionTag = () => {
  if (solutionToAdd.value !== '') {
    const index = parseInt(solutionToAdd.value);
    if (!selectedSolutionsForExport.value.includes(index)) {
      selectedSolutionsForExport.value.push(index);
    }
    solutionToAdd.value = ''; // 重置下拉菜单
  }
};

// 移除方案标签
const removeSolutionTag = (index: number) => {
  const position = selectedSolutionsForExport.value.indexOf(index);
  if (position > -1) {
    selectedSolutionsForExport.value.splice(position, 1);
  }
};

// 导出选中的优化方案
const exportSelectedSolutions = () => {
  if (selectedSolutionsForExport.value.length === 0) {
    alert(currentLanguage.value === 'zh' ? '请先选择要导出的方案' : 'Please select solutions to export');
    return;
  }

  if (paretoSolutions.value.length === 0) {
    alert(currentLanguage.value === 'zh' ? '没有可用的优化方案数据' : 'No solution data available');
    return;
  }

  // 对每个选中的方案单独导出
  selectedSolutionsForExport.value.forEach(solutionIndex => {
    const solution = paretoSolutions.value[solutionIndex];

    if (!solution) {
      console.warn(`方案${solutionIndex}不存在`);
      return;
    }

    // 创建CSV内容
    let csvContent = '';

    // 添加方案概览信息
    csvContent += `Solution Index,${solutionIndex}\n`;
    csvContent += `Total Energy,${solution.energy || 'N/A'}\n`;
    csvContent += `Total Cost,${solution.cost || 'N/A'}\n`;
    csvContent += '\n'; // 空行分隔

    // 如果有节点数据
    if (solution.nodes && Array.isArray(solution.nodes) && solution.nodes.length > 0) {
      // 获取第一个节点的所有键作为表头（保持顺序）
      const firstNode = solution.nodes[0];
      const keys = Object.keys(firstNode);
      const headers = ['Node Index', ...keys];
      csvContent += headers.join(',') + '\n';

      // 遍历每个节点，导出所有字段
      for (let nodeIndex = 0; nodeIndex < solution.nodes.length; nodeIndex++) {
        const node = solution.nodes[nodeIndex];
        const row: string[] = [String(nodeIndex)];

        // 按照keys的顺序提取每个节点的值
        keys.forEach(key => {
          const value = node[key];

          // CSV格式化：处理特殊字符
          if (value === undefined || value === null) {
            row.push('');
          } else if (typeof value === 'string') {
            // 字符串类型需要检查是否包含特殊字符：逗号、换行符、引号
            if (value.includes(',') || value.includes('\n') || value.includes('\r') || value.includes('"')) {
              // 将字符串中的引号转义（双引号变成两个引号），然后用引号包裹整个字符串
              const escapedValue = value.replace(/"/g, '""');
              row.push(`"${escapedValue}"`);
            } else {
              row.push(value);
            }
          } else {
            // 数字或其他类型直接转换为字符串
            row.push(String(value));
          }
        });

        csvContent += row.join(',') + '\n';
      }
    }

    // 创建Blob并下载
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const fileName = `solution_${solutionIndex}.csv`;
    saveAs(blob, fileName);
  });

  console.log(`成功导出${selectedSolutionsForExport.value.length}个优化方案`);
};

// 切换帮助面板显示状态
const toggleHelpPanel = () => {
  showHelpPanel.value = !showHelpPanel.value;
};

// 计算对比直方图的高度
const getComparisonBarWidth = (value: number | undefined, type: string): string => {
  if (value === undefined || value === null) return '10px';

  // 根据不同参数类型设置最大值范围
  let maxValue = 1;
  switch (type) {
    case 'Con':
      maxValue = 2; // 导热系数最大值2
      break;
    case 'Thi':
      maxValue = 0.5; // 厚度最大值0.5
      break;
    case 'SA':
    case 'SCon':
    case 'SSHGC':
      maxValue = 1; // 其他参数最大值1
      break;
  }

  const percentage = Math.min((value / maxValue) * 75, 75); // 最大50px高度
  return `${Math.max(percentage, 15)}px`; // 最小10px高度
};

// 计算对比直方图的颜色
const getComparisonBarColor = (beforeValue: number, afterValue: number | undefined): string => {
  if (afterValue === undefined || afterValue === null) return '#87CEEB'; // 淡蓝色

  if (afterValue > beforeValue) {
    return '#FF6B6B'; // 红色 - 增大
  } else if (afterValue < beforeValue) {
    return '#4CAF50'; // 绿色 - 减小
  } else {
    return '#87CEEB'; // 淡蓝色 - 不变
  }
};

// 切换语言函数
const toggleLanguage = () => {
  currentLanguage.value = currentLanguage.value === 'zh' ? 'en' : 'zh';
  console.log('语言已切换为:', currentLanguage.value);
};

// 处理返回按钮点击
const handleBackButton = () => {
  // 显示确认弹窗
  if (window.confirm(currentLanguage.value === 'zh' ? '确定返回上一步吗？' : 'Are you sure you want to go back?')) {
    // 保存当前的面组数据到localStorage
    if (faceGroups.value.length > 0) {
      localStorage.setItem('faceGroupsData', JSON.stringify(faceGroups.value));
      console.log('返回ThirdView前已保存面组数据');
    }
    // 用户确认后，导航到ThirdView页面
    router.push('/third');
  }
};

// 加载墙体材料数据
const loadWallMaterials = async () => {
  try {
    const response = await fetch('/materials/wall_select.xlsx');
    const arrayBuffer = await response.arrayBuffer();
    const workbook = XLSX.read(arrayBuffer, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    const jsonData = XLSX.utils.sheet_to_json(worksheet) as {Material: string, MaterialEN: string, Con: number, Price: number}[];

    wallMaterials.value = jsonData;
    console.log('成功加载墙体材料数据:', jsonData);
  } catch (error) {
    console.error('加载墙体材料数据失败:', error);
    // 如果加载失败，使用默认数据
    wallMaterials.value = [
      { Material: '混凝土', MaterialEN: 'Concrete', Con: 1.74, Price: 100 },
      { Material: '砖墙', MaterialEN: 'Brick Wall', Con: 0.81, Price: 80 },
      { Material: '钢结构', MaterialEN: 'Steel Structure', Con: 50, Price: 200 }
    ];
  }
};

// 开始优化
const startOptimization = async () => {
  console.log('开始优化，参数:', optimizationParams.value);
  if (wallMaterials.value[optimizationParams.value.wallMaterial]) {
    console.log('选中的材料:', wallMaterials.value[optimizationParams.value.wallMaterial]);
  }

  // 设置加载状态
  isLoading.value = true;

  try {
    const optResponse = await sendJsonToLocalServer();
    console.log('优化请求响应:', optResponse);

    // 检查请求是否成功
    if (!optResponse.success) {
      // 显示错误信息
      alert(optResponse.message || '优化请求失败，请检查后端服务是否正常运行');
      console.error('优化失败:', optResponse.message);
      return;
    }

    // 如果优化成功，更新pareto_solutions数据
    if (optResponse.data && optResponse.data.pareto_solutions) {
      paretoSolutions.value = optResponse.data.pareto_solutions;
      console.log('更新Pareto优化方案数据:', paretoSolutions.value.length, '个方案');

      // 输出一些数据点用于调试
      paretoSolutions.value.forEach((solution, index) => {
        console.log(`方案${index}: 价格=${solution.cost.toFixed(2)}, 能耗=${solution.energy.toFixed(2)}`);
      });
      
      // 显示成功信息
      if (paretoSolutions.value.length > 0) {
        console.log(`优化完成！找到 ${paretoSolutions.value.length} 个帕累托最优解`);
      }
    } else {
      const errorMsg = optResponse.data?.error || '优化响应中没有pareto_solutions数据';
      console.warn(errorMsg);
      alert(errorMsg);
    }
  } catch (error: any) {
    const errorMessage = error.message || '优化请求失败，请检查网络连接和后端服务';
    console.error('优化请求失败:', error);
    alert(errorMessage);
  } finally {
    // 无论成功还是失败，都要清除加载状态
    isLoading.value = false;
  }
};

// 选择方案
const selectSolution = (solution: {cost: number, energy: number, nodes: any[]}, index: number) => {
  selectedSolution.value = solution;
  selectedSolutionIndex.value = index;
  console.log('选中方案:', index, solution);
};

// 跳转到优化分析页面
const goToOptView = () => {
  router.push('/opt');
};

// 显示立方体面
const showCubeFaces = () => {
  if (showIntersections.value || showClippedFaces.value) {
    showIntersections.value = false;
    showClippedFaces.value = false;
    console.log('切换到立方体面显示模式');
    updateFacesVisibility();
  }
};

// 显示交集面
const showIntersectionFaces = () => {
  if (!showIntersections.value) {
    showIntersections.value = true;
    showClippedFaces.value = false;
    console.log('切换到交集面显示模式');
    updateFacesVisibility();
  } else {
    // 如果已经是交集面模式，则切换回立方体面模式
    showIntersections.value = false;
    showClippedFaces.value = false;
    console.log('切换到立方体面显示模式');
    updateFacesVisibility();
  }
};

// 显示裁剪面
const toggleClippedFaces = () => {
  if (!showClippedFaces.value) {
    showIntersections.value = false;
    showClippedFaces.value = true;
    console.log('切换到裁剪面显示模式');
    updateFacesVisibility();
  } else {
    // 如果已经是裁剪面模式，则切换回立方体面模式
    showIntersections.value = false;
    showClippedFaces.value = false;
    console.log('切换到立方体面显示模式');
    updateFacesVisibility();
  }
};

// 清除选中状态
const clearSelection = () => {
  if (selectedFace) {
    // 恢复选中面的原始颜色
    const originalColor = originalColors.get(selectedFace);
    if (originalColor !== undefined && selectedFace.material instanceof THREE.MeshStandardMaterial) {
      (selectedFace.material.color as any).setHex(originalColor);
    }

    // 如果是裁剪面，恢复同组所有面的颜色
    if (showClippedFaces.value && !selectedFace.userData.isIntersection) {
      const faceIndex = selectedFace.userData.faceIndex;
      const groupIndex = clippedFaceGroups.findIndex(group => group.includes(faceIndex));

      if (groupIndex !== -1) {
        const group = clippedFaceGroups[groupIndex];
        group.forEach(idx => {
          if (idx !== faceIndex) { // 跳过当前选中的面，因为它已经被上面处理过了
            const groupMesh = clippedFaceMeshes[idx];
            if (groupMesh && groupMesh.material instanceof THREE.MeshStandardMaterial) {
              const originalColor = originalColors.get(groupMesh);
              if (originalColor !== undefined) {
                (groupMesh.material.color as any).setHex(originalColor);
                // 从originalColors中移除，防止内存泄漏
                originalColors.delete(groupMesh);
              }
            }
          }
        });
      }
    }

    // 从originalColors中移除选中面，防止内存泄漏
    originalColors.delete(selectedFace);

    selectedFace = null;
    selectedFaceInfo.value = null;
  }

  // 清除选中的窗口
  if (selectedWindowMesh.value && upperScene) {
    // 移除窗口边框
    if (windowSelectionBorder) {
      upperScene.remove(windowSelectionBorder);
      windowSelectionBorder = null;
    }

    // 清除选中状态
    selectedWindowMesh.value = null;

    // 隐藏窗口信息提示
    showWindowInfoTooltip.value = false;
    selectedWindowInfo.value = null;
  }

  // 移除主边框
  if (selectionBorder && scene) {
    scene.remove(selectionBorder);
    selectionBorder = null;
  }

  // 移除同组面的所有边框
  if (groupSelectionBorders.length > 0 && scene) {
    groupSelectionBorders.forEach(border => {
      scene.remove(border);
    });
    groupSelectionBorders = [];
  }
};

// 更新面的可见性
const updateFacesVisibility = () => {
  // 在切换显示模式前，确保清除所有高亮状态
  clearSelection();

  // 显示/隐藏立方体面
  cubeFaceMeshes.forEach(mesh => {
    (mesh as any).visible = !showIntersections.value && !showClippedFaces.value;
  });

  // 显示/隐藏交集面
  intersectionFaceMeshes.forEach(mesh => {
    (mesh as any).visible = showIntersections.value;
  });

  // 显示/隐藏裁剪面
  clippedFaceMeshes.forEach(mesh => {
    (mesh as any).visible = showClippedFaces.value;
  });
};

// 从localStorage加载立方体数据
const loadCubesData = (): CubeData[] => {
  try {
    const savedModelData = localStorage.getItem('modelData');
    if (savedModelData) {
      const modelData = JSON.parse(savedModelData);
      if (modelData.cubes && Array.isArray(modelData.cubes)) {
        console.log('成功加载立方体数据:', modelData.cubes.length, '个立方体');
        return modelData.cubes;
      }
    }
  } catch (error) {
    console.error('加载立方体数据失败:', error);
  }

  console.warn('未找到立方体数据或数据格式不正确');
  return [];
};

// 渲染立方体的面
const renderCubeFaces = (cubesData: CubeData[]) => {
  if (!scene) return;

  // 清除场景中现有的面
  scene.children = scene.children.filter(child => {
    const isFace = child.userData && child.userData.isFace;
    if (isFace && child instanceof THREE.Mesh) {
      if (child.geometry) {
        (child.geometry as any).dispose();
      }
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(m => (m as any).dispose());
        } else {
          (child.material as any).dispose();
        }
      }
    }
    return !isFace;
  });

  // 如果没有立方体数据，则不渲染
  if (cubesData.length === 0) {
    console.warn('没有立方体数据可渲染');
    return;
  }

  // 将立方体转换为面
  allCubeFaces = cubesToFaces(cubesData);
  console.log(`生成了 ${allCubeFaces.length} 个立方体面`);

  // 输出每个立方体面的法向量，用于调试
  allCubeFaces.forEach((face, index) => {
    const cubeIndex = Math.floor(index / 6);
    const normal = face.normal;
    console.log(`立方体 ${cubeIndex} 面 ${index % 6}: 法向量 (${normal.x}, ${normal.y}, ${normal.z})`);
  });

  // 计算所有面的交集
  console.log('计算面的交集...');
  console.time('计算交集');
  intersectionFaces = findAllFaceIntersections(allCubeFaces);
  console.timeEnd('计算交集');
  console.log(`找到 ${intersectionFaces.length} 个交集面`);

  // 输出每个交集面的详细信息，用于调试
  intersectionFaces.forEach((face, index) => {
    const normal = face.normal;
    const area = calculateFaceArea(face.vertices);
    console.log(`交集面 ${index}: ${face.vertices.length} 个顶点, 法向量 (${normal.x}, ${normal.y}, ${normal.z}), 面积 ${area.toFixed(6)}`);

    // 输出顶点坐标
    face.vertices.forEach((v, i) => {
      console.log(`  顶点 ${i}: (${v.x.toFixed(3)}, ${v.y.toFixed(3)}, ${v.z.toFixed(3)})`);
    });
  });

  // 计算裁剪后的面
  console.log('计算裁剪面...');
  console.time('计算裁剪面');
  clippedFaces = computeAllClippedFaces(allCubeFaces, intersectionFaces);
  console.timeEnd('计算裁剪面');
  console.log(`生成了 ${clippedFaces.length} 个裁剪面`);

  // 对裁剪面进行分组
  console.log('对裁剪面进行分组...');
  console.time('裁剪面分组');
  clippedFaceGroups = groupConnectedClippedFaces(clippedFaces);
  console.timeEnd('裁剪面分组');
  console.log(`裁剪面分为 ${clippedFaceGroups.length} 个组`);

  // 输出每个组的信息
  clippedFaceGroups.forEach((group, index) => {
    console.log(`组 ${index}: 包含 ${group.length} 个裁剪面，索引: ${group.join(', ')}`);
  });

  // 生成面组数据
  loadFaceGroupsFromStorage();

  // 渲染立方体面
  console.time('渲染立方体面');
  cubeFaceMeshes = renderFacesInScene(scene, allCubeFaces);
  console.timeEnd('渲染立方体面');

  // 渲染交集面
  console.time('渲染交集面');
  intersectionFaceMeshes = renderFacesInScene(scene, intersectionFaces, true);
  console.timeEnd('渲染交集面');

  // 渲染裁剪面
  console.time('渲染裁剪面');
  clippedFaceMeshes = renderFacesInScene(scene, clippedFaces, false);
  console.timeEnd('渲染裁剪面');

  // 根据当前显示模式设置面的可见性
  updateFacesVisibility();

  // 清除选中状态
  selectedFace = null;
  originalColors.clear();
  selectedFaceInfo.value = null;

  // 移除边框
  if (selectionBorder && scene) {
    scene.remove(selectionBorder);
    selectionBorder = null;
  }

  // 输出渲染结果
  console.log(`渲染了 ${cubeFaceMeshes.length} 个立方体面, ${intersectionFaceMeshes.length} 个交集面和 ${clippedFaceMeshes.length} 个裁剪面`);
};

// 计算面的面积
const calculateFaceArea = (vertices: THREE.Vector3[]): number => {
  if (vertices.length < 3) return 0;

  // 使用类型断言解决类型错误
  const Triangle = (THREE as any).Triangle;

  if (vertices.length === 4) {
    // 对于四边形，将其分解为两个三角形
    const triangle1 = new Triangle(vertices[0], vertices[1], vertices[2]);
    const triangle2 = new Triangle(vertices[0], vertices[2], vertices[3]);

    // 计算两个三角形的面积之和
    return triangle1.getArea() + triangle2.getArea();
  } else {
    // 对于任意多边形，使用扇形三角化
    let totalArea = 0;
    const center = new THREE.Vector3(0, 0, 0);

    // 计算中心点
    vertices.forEach(v => {
      center.x += v.x;
      center.y += v.y;
      center.z += v.z;
    });
    center.x /= vertices.length;
    center.y /= vertices.length;
    center.z /= vertices.length;

    // 将多边形分解为三角形，并计算面积
    for (let i = 0; i < vertices.length; i++) {
      const v1 = vertices[i];
      const v2 = vertices[(i + 1) % vertices.length];

      // 创建三角形：中心点、当前顶点、下一个顶点
      const triangle = new Triangle(center, v1, v2);
      totalArea += triangle.getArea();
    }

    return totalArea;
  }
};

// 计算面的周长
const calculateFacePerimeter = (vertices: THREE.Vector3[], faceIndices?: number[]): number => {
  if (vertices.length < 3) return 0;

  // 提取所有顶点的x、y坐标
  const xCoords = vertices.map(v => v.x);
  const yCoords = vertices.map(v => v.y);

  // 找出面组的包围盒
  const minX = Math.min(...xCoords);
  const maxX = Math.max(...xCoords);
  const minY = Math.min(...yCoords);
  const maxY = Math.max(...yCoords);

  // 计算宽度和高度
  const widths = [maxX - minX];
  const heights = [maxY - minY];

  // 使用提供的方法计算周长
  const totalWidth = widths.reduce((sum, w) => sum + w, 0);

  // 如果只有一个高度，则没有相邻高度差
  let sumDiff = 0;
  if (heights.length > 1) {
    for (let i = 0; i < heights.length - 1; i++) {
      sumDiff += Math.abs(heights[i] - heights[i + 1]);
    }
  }

  const perimeter = 2 * totalWidth + heights[0] + heights[heights.length - 1] + sumDiff;

  return perimeter;
};

// 计算面组的周长，考虑所有子面
const calculateFaceGroupPerimeter = (group: FaceGroup): number => {
  // 收集所有子面的高度和宽度
  const heights: number[] = [];
  const widths: number[] = [];

  // 获取面组的法向量方向
  const direction = group.direction;

  // 处理交集面
  if (group.type === '交集面') {
    // 对于单个交集面，直接使用其顶点
    const xCoords = group.vertices.map(v => v.x);
    const yCoords = group.vertices.map(v => v.y);
    const zCoords = group.vertices.map(v => v.z);

    const minX = Math.min(...xCoords);
    const maxX = Math.max(...xCoords);
    const minY = Math.min(...yCoords);
    const maxY = Math.max(...yCoords);
    const minZ = Math.min(...zCoords);
    const maxZ = Math.max(...zCoords);

    // 根据面的朝向确定宽度和高度
    if (direction.includes('左面') || direction.includes('右面')) {
      // 法向量是x，使用z作为宽度，y作为高度
      widths.push(maxZ - minZ);
      heights.push(maxY - minY);
    } else if (direction.includes('下面') || direction.includes('上面')) {
      // 法向量是y，使用x作为宽度，z作为高度
      widths.push(maxX - minX);
      heights.push(maxZ - minZ);
    } else {
      // 法向量是z，使用x作为宽度，y作为高度
      widths.push(maxX - minX);
      heights.push(maxY - minY);
    }
  }
  // 处理裁剪面组
  else if (group.type === '裁剪面组' && group.faceIndices.length > 0) {
    // 对于裁剪面组，遍历所有子面
    group.faceIndices.forEach(faceIndex => {
      const face = clippedFaces[faceIndex];
      const xCoords = face.vertices.map(v => v.x);
      const yCoords = face.vertices.map(v => v.y);
      const zCoords = face.vertices.map(v => v.z);

      const minX = Math.min(...xCoords);
      const maxX = Math.max(...xCoords);
      const minY = Math.min(...yCoords);
      const maxY = Math.max(...yCoords);
      const minZ = Math.min(...zCoords);
      const maxZ = Math.max(...zCoords);

      // 根据面的朝向确定宽度和高度
      if (direction.includes('左面') || direction.includes('右面')) {
        // 法向量是x，使用z作为宽度，y作为高度
        widths.push(maxZ - minZ);
        heights.push(maxY - minY);
      } else if (direction.includes('下面') || direction.includes('上面')) {
        // 法向量是y，使用x作为宽度，z作为高度
        widths.push(maxX - minX);
        heights.push(maxZ - minZ);
      } else {
        // 法向量是z，使用x作为宽度，y作为高度
        widths.push(maxX - minX);
        heights.push(maxY - minY);
      }
    });
  }



  // 使用提供的方法计算周长
  const totalWidth = widths.reduce((sum, w) => sum + w, 0);

  // 计算相邻高度差之和
  let sumDiff = 0;
  if (heights.length > 1) {
    for (let i = 0; i < heights.length - 1; i++) {
      sumDiff += Math.abs(heights[i] - heights[i + 1]);
    }
  }

  const perimeter = 2 * totalWidth + heights[0] + heights[heights.length - 1] + sumDiff;

  return perimeter;
};

// 获取法向量的方向描述
const getNormalDirection = (normal: THREE.Vector3): string => {
  const x = Math.round(normal.x);
  const y = Math.round(normal.y);
  const z = Math.round(normal.z);

  if (x === -1 && y === 0 && z === 0) return directionMap['x-1'];
  if (x === 1 && y === 0 && z === 0) return directionMap['x+1'];
  if (x === 0 && y === -1 && z === 0) return directionMap['y-1'];
  if (x === 0 && y === 1 && z === 0) return directionMap['y+1'];
  if (x === 0 && y === 0 && z === -1) return directionMap['z-1'];
  if (x === 0 && y === 0 && z === 1) return directionMap['z+1'];

  return `未知方向 (${x}, ${y}, ${z})`;
};

// 创建选中面的红色边框
const createSelectionBorder = (mesh: THREE.Mesh, color: number = 0xff0000, targetScene: THREE.Scene | null = scene) => {
  if (!targetScene) return null;

  // 获取面的顶点
  const vertices = mesh.userData.vertices;
  if (!vertices || vertices.length < 3) return null;

  // 创建边框几何体
  const geometry = new THREE.BufferGeometry();
  const positions: number[] = [];

  // 添加每条边的顶点
  for (let i = 0; i < vertices.length; i++) {
    const v1 = vertices[i];
    const v2 = vertices[(i + 1) % vertices.length];

    positions.push(v1.x, v1.y, v1.z);
    positions.push(v2.x, v2.y, v2.z);
  }

  // 设置几何体的顶点
  (geometry as any).setAttribute(
    'position',
    new (THREE as any).Float32BufferAttribute(positions, 3)
  );

  // 创建线条材质
  const material = new THREE.LineBasicMaterial({
    color: color,
    linewidth: 2
  });

  // 创建线段对象
  const border = new THREE.LineSegments(geometry, material);

  // 设置渲染顺序，确保边框显示在面的上方
  (border as any).renderOrder = 2;

  // 添加到场景
  targetScene.add(border);

  return border;
};

// 处理鼠标点击事件
const onMouseClick = (event: MouseEvent) => {
  if (!canvasRef.value || !scene || !camera) return;

  // 计算鼠标在画布中的位置
  const rect = canvasRef.value.getBoundingClientRect();
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;

  // 将鼠标位置归一化为设备坐标（-1到1之间）
  mouse.x = (x / rect.width) * 2 - 1;
  mouse.y = -(y / rect.height) * 2 + 1;

  // 设置射线投射器
  raycaster.setFromCamera(mouse, camera);

  // 获取与射线相交的对象
  // 过滤出只有可见的面的对象进行检测
  const faceMeshes = scene.children.filter(child =>
    child.userData &&
    child.userData.isFace &&
    (child as any).visible
  );

  const intersects = raycaster.intersectObjects(faceMeshes, false);

  // 如果有相交的对象
  if (intersects.length > 0) {
    // 获取第一个相交的对象
    const intersectedObject = intersects[0].object;

    // 检查是否是面
    if (intersectedObject instanceof THREE.Mesh &&
        intersectedObject.userData &&
        intersectedObject.userData.isFace) {

      // 获取面的信息
      const faceIndex = intersectedObject.userData.faceIndex;
      const isIntersection = intersectedObject.userData.isIntersection || false;
      const isClipped = showClippedFaces.value && !isIntersection;

      // 查找对应的面组索引并调用highlightGroup
      if (isIntersection) {
        // 查找对应的交集面组索引
        const groupIndex = faceGroups.value.findIndex(group =>
          group.type === '交集面' && group.faceIndices[0] === faceIndex
        );

        if (groupIndex !== -1) {
          // 调用highlightGroup函数，与表格中的"查看"按钮行为一致
          highlightGroup(groupIndex);
        }
      } else if (isClipped) {
        // 查找对应的裁剪面组索引
        const clippedGroupIndex = clippedFaceGroups.findIndex(group => group.includes(faceIndex));

        if (clippedGroupIndex !== -1) {
          // 查找对应的面组在faceGroups中的索引
          const groupIndex = faceGroups.value.findIndex(group =>
            group.type === '裁剪面组' && group.index === clippedGroupIndex
          );

          if (groupIndex !== -1) {
            // 调用highlightGroup函数，与表格中的"查看"按钮行为一致
            highlightGroup(groupIndex);
          }
        }
      } else {
        // 如果是立方体原始面，目前不支持在表格中显示，清除选择
        clearSelection();
      }

      console.log(`选中了${isIntersection ? '交集' : ''}面 ${faceIndex}`);
    }
  } else {
    // 如果点击了空白区域，清除选择
    clearSelection();
  }
};

// 初始化场景
const initScene = () => {
  if (!canvasRef.value) return;

  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  // 创建相机 - 使用正交相机实现真正的等轴侧视图
  const container = document.querySelector('.viewport-container') as HTMLElement;
  const width = container ? container.clientWidth : window.innerWidth * 0.475;
  const height = container ? container.clientHeight : window.innerHeight * 0.95;
  const aspect = width / height;

  const viewSize = 10;
  camera = new (THREE as any).OrthographicCamera(
    -viewSize * aspect / 2, // left
    viewSize * aspect / 2,  // right
    viewSize / 2,           // top
    -viewSize / 2,          // bottom
    0.1,                    // near
    1000                    // far
  );

  // 设置相机位置为等轴侧视图
  const distance = 10;
  camera.position.set(distance, distance, distance);
  camera.lookAt(0, 0, 0);

  // 确保相机的上方向是Y轴
  (camera as any).up.set(0, 1, 0);

  // 更新相机的投影矩阵
  camera.updateProjectionMatrix();

  // 创建渲染器
  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true
  });

  // 设置渲染器尺寸
  if (container) {
    renderer.setSize(width, height);
    console.log('设置渲染器尺寸:', width, height);
  } else {
    renderer.setSize(window.innerWidth * 0.475, window.innerHeight * 0.95);
    console.log('未找到容器，使用窗口尺寸的47.5%宽度');
  }
  renderer.setPixelRatio(window.devicePixelRatio);

  // 添加光源
  const ambientLight = new THREE.AmbientLight(0x404040);
  scene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
  directionalLight.position.set(1, 1, 1);
  scene.add(directionalLight);

  // 添加坐标网格
  const gridHelper = new THREE.GridHelper(10, 10);
  scene.add(gridHelper);

  // 添加坐标轴
  const axesHelper = new THREE.AxesHelper(5);
  scene.add(axesHelper);

  // 初始化射线投射器和鼠标位置
  raycaster = new THREE.Raycaster();
  // 设置射线检测的精度，确保能够检测到所有面
  (raycaster.params as any).Mesh.threshold = 0.1;
  mouse = new THREE.Vector2();

  // 添加鼠标点击事件监听
  canvasRef.value.addEventListener('click', onMouseClick);

  // 初始化控制器
  orbitControls = new OrbitControls(camera, renderer.domElement);
  orbitControls.enableDamping = true;

  // 设置控制方式 - 中键平移，右键旋转
  orbitControls.mouseButtons = {
    LEFT: null,   // 左键不做任何操作，由我们自己处理
    MIDDLE: 2,    // 中键平移 (2 = PAN)
    RIGHT: 0      // 右键旋转 (0 = ROTATE)
  };

  // 允许缩放
  orbitControls.enableZoom = true;

  // 加载并渲染立方体面
  const cubesData = loadCubesData();
  renderCubeFaces(cubesData);

  // 开始动画循环
  animate();
};

// 窗口大小调整
const onWindowResize = () => {
  if (!camera || !renderer) return;

  const container = document.querySelector('.viewport-container') as HTMLElement;
  if (container) {
    const width = container.clientWidth;
    const height = container.clientHeight;
    console.log('窗口大小调整:', width, height);

    // 更新相机
    const aspect = width / height;
    const viewSize = 10;

    // 根据相机类型更新参数
    if ((camera as any).isOrthographicCamera) {
      (camera as any).left = -viewSize * aspect / 2;
      (camera as any).right = viewSize * aspect / 2;
      (camera as any).top = viewSize / 2;
      (camera as any).bottom = -viewSize / 2;
    } else {
      // 透视相机
      camera.aspect = aspect;
    }

    camera.updateProjectionMatrix();

    // 更新渲染器尺寸
    renderer.setSize(width, height);
  } else {
    // 如果找不到容器，使用窗口尺寸的47.5%宽度
    const width = window.innerWidth * 0.475;
    const height = window.innerHeight * 0.95;

    // 更新相机
    const aspect = width / height;
    const viewSize = 10;

    if ((camera as any).isOrthographicCamera) {
      (camera as any).left = -viewSize * aspect / 2;
      (camera as any).right = viewSize * aspect / 2;
      (camera as any).top = viewSize / 2;
      (camera as any).bottom = -viewSize / 2;
    } else {
      camera.aspect = aspect;
    }

    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  }

  // 更新右上视口
  if (upperCamera && upperRenderer) {
    const upperContainer = document.querySelector('.upper-panel') as HTMLElement;
    if (upperContainer) {
      const width = upperContainer.clientWidth;
      const height = upperContainer.clientHeight - 40; // 减去标题栏高度

      // 更新相机
      const aspect = width / height;
      const viewSize = 10;

      // 根据相机类型更新参数
      if ((upperCamera as any).isOrthographicCamera) {
        (upperCamera as any).left = -viewSize * aspect / 2;
        (upperCamera as any).right = viewSize * aspect / 2;
        (upperCamera as any).top = viewSize / 2;
        (upperCamera as any).bottom = -viewSize / 2;
      } else {
        // 透视相机
        upperCamera.aspect = aspect;
      }

      upperCamera.updateProjectionMatrix();

      // 更新渲染器尺寸
      upperRenderer.setSize(width, height);
    }
  }
};

// 动画循环
const animate = () => {
  requestAnimationFrame(animate);
  orbitControls.update();
  renderer.render(scene, camera);

  // 渲染右上视口
  if (upperRenderer && upperScene && upperCamera) {
    upperOrbitControls?.update();
    upperRenderer.render(upperScene, upperCamera);
  }
};

// 浏览器关闭事件处理函数
const handleBeforeUnload = () => {
  localStorage.removeItem('faceGroupsData');
  localStorage.removeItem('modelData');
  console.log('浏览器关闭，已清理所有数据');
};

// 组件挂载时初始化
onMounted(() => {
  console.log('OptView组件已挂载');

  // 监听浏览器关闭事件，清理数据
  window.addEventListener('beforeunload', handleBeforeUnload);

  // 加载墙体材料数据
  loadWallMaterials();

  // 确保DOM已完全渲染
  nextTick(() => {
    initScene();
    initUpperScene();
    initDrawingEvents(); // 初始化绘制事件

    // 添加窗口大小调整监听
    window.addEventListener('resize', onWindowResize);

    // 移除鼠标移动事件监听，使信息栏固定在点击位置
    // document.addEventListener('mousemove', (event) => {
    //   if (showWindowInfoTooltip.value) {
    //     windowInfoPosition.value = {
    //       x: event.clientX + 10,
    //       y: event.clientY - 10
    //     };
    //   }
    // });

    // 确保初始化后立即调整大小
    setTimeout(() => {
      onWindowResize();
      console.log('初始调整大小完成');
    }, 100);
  });

  // 在组件挂载时从路由参数获取API返回数据
  if (route.query.response) {
    try {
      apiResponse.value = JSON.parse(route.query.response as string);
      console.log('解析到API返回数据:', apiResponse.value);

      // 提取pareto_solutions数据
      if (apiResponse.value.pareto_solutions && Array.isArray(apiResponse.value.pareto_solutions)) {
        paretoSolutions.value = apiResponse.value.pareto_solutions;
        console.log('提取到Pareto优化方案数据:', paretoSolutions.value.length, '个方案');
      }
    } catch (error) {
      console.error('解析API返回数据失败:', error);
      apiResponse.value = { error: '解析API返回数据失败' };
    }
  } else {
    console.log('未找到API返回数据');
    apiResponse.value = { message: '未找到API返回数据' };
  }
});

// 组件卸载前清理
onBeforeUnmount(() => {
  console.log('第二页组件卸载，清理资源');
  window.removeEventListener('resize', onWindowResize);

  // 移除浏览器关闭事件监听
  window.removeEventListener('beforeunload', handleBeforeUnload);

  // 移除鼠标点击事件监听
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('click', onMouseClick);
  }

  // 移除绘制相关事件监听
  if (upperCanvasRef.value) {
    upperCanvasRef.value.removeEventListener('mousedown', handleDrawMouseDown);
    upperCanvasRef.value.removeEventListener('mousemove', handleDrawMouseMove);
    upperCanvasRef.value.removeEventListener('mouseup', handleDrawMouseUp);
    upperCanvasRef.value.removeEventListener('click', onUpperCanvasClick);
  }

  // 移除鼠标移动事件监听（已注释掉，不需要移除）
  // document.removeEventListener('mousemove', () => {});

  // 释放资源
  if (renderer) {
    renderer.dispose();
  }

  if (upperRenderer) {
    upperRenderer.dispose();
  }

  // 清除选中状态
  selectedFace = null;
  originalColors.clear();
  selectedFaceInfo.value = null;
  selectedWindowMesh.value = null;

  // 移除边框
  if (selectionBorder && scene) {
    scene.remove(selectionBorder);
    selectionBorder = null;
  }

  // 移除门窗边框
  if (windowSelectionBorder && upperScene) {
    upperScene.remove(windowSelectionBorder);
    windowSelectionBorder = null;
  }

  // 移除同组面的所有边框
  if (groupSelectionBorders.length > 0 && scene) {
    groupSelectionBorders.forEach(border => {
      scene.remove(border);
    });
    groupSelectionBorders = [];
  }
});

// 从localStorage加载面组数据
const loadFaceGroupsFromStorage = () => {
  try {
    const savedFaceGroups = localStorage.getItem('faceGroupsData');
    if (savedFaceGroups) {
      const parsedFaceGroups = JSON.parse(savedFaceGroups);
      if (Array.isArray(parsedFaceGroups)) {
        faceGroups.value = parsedFaceGroups;
        console.log('从localStorage成功加载面组数据，包含', faceGroups.value.length, '个面组');

        // 转换门窗位置数据格式
        faceGroups.value = parsedFaceGroups.map(group => ({
          ...group,
          windows: group.windows?.map((window: any) => ({
            ...window,
            position: window.position.x !== undefined ?
              new THREE.Vector3(window.position.x, window.position.y, window.position.z) :
              window.position
          })) || []
        }));

        // 输出门窗信息用于调试
        faceGroups.value.forEach((group, index) => {
          if (group.windows && group.windows.length > 0) {
            console.log(`面组${index}包含${group.windows.length}个门窗`);
          }
        });

        // 渲染所有面组的门窗到3D视图
        renderAllWindowsTo3DView();
        return;
      }
    }
  } catch (error) {
    console.error('从localStorage加载面组数据失败:', error);
  }

  // 如果加载失败，则生成新的面组数据
  console.log('localStorage中没有面组数据，重新生成');
  generateFaceGroups();
};

// 计算并生成面组数据
const generateFaceGroups = () => {
  console.log('生成面组数据...');

  // 清空原有面组数据
  faceGroups.value = [];

  // 添加交集面作为面组
  for (let i = 0; i < intersectionFaces.length; i++) {
    const face = intersectionFaces[i];
    // 只有包含顶点的面才添加
    if (face.vertices.length >= 3) {
      const area = calculateFaceArea(face.vertices);

      // 使用更小的阈值，跳过面积太小的交集面
      const AREA_THRESHOLD = 0.01;
      if (area < AREA_THRESHOLD) {
        continue;
      }

      const faceGroup: FaceGroup = {
        index: i,
        type: '交集面',
        direction: '0',
        area: area,
        perimeter: 0, // 临时值，后面会更新
        shapeCoefficient: 0, // 临时值，后面会更新
        subFaceTypeCoefficient: 0, // 初始值为0，表示无门窗
        subFaceTotalArea: 0, // 初始值为0，表示无子面面积
        subFaceUValue: 0, // 初始值为0，表示无子面
        subFaceSHGC: 0, // 初始值为0，表示无子面
        conductivity: 1, // 导热系数默认为1
        thickness: 0.2, // 厚度默认为0.2
        longwaveAbsorptance: 0.9, // 长波辐射吸收比默认为0.9
        solarAbsorptance: 0.7, // 太阳辐射吸收比默认为0.7
        visibleAbsorptance: 0.7, // 可见光辐射吸收比默认为0.7
        vertexCount: face.vertices.length,
        vertices: face.vertices,
        faceIndices: [i],
        windows: [], // 初始化空的windows数组
        category: 'interior', // 设置大类为interior
        regionClass: 0, // 设置区域类默认值为0
        externalCondition: 'Surface' // 设置外接条件
      };

      // 计算并设置周长
      faceGroup.perimeter = calculateFaceGroupPerimeter(faceGroup);

      // 计算并设置形状系数
      faceGroup.shapeCoefficient = calculateShapeCoefficient(faceGroup.perimeter, faceGroup.area);

      faceGroups.value.push(faceGroup);
    }
  }

  // 添加裁剪面组
  for (let i = 0; i < clippedFaceGroups.length; i++) {
    const group = clippedFaceGroups[i];
    // 只有包含面的组才添加
    if (group.length > 0) {
      // 获取组内第一个面的法向量
      const firstFace = clippedFaces[group[0]];
      const normal = firstFace.normal;

      // 计算组的总面积和收集所有顶点
      let totalArea = 0;
      const allVertices: THREE.Vector3[] = [];

      group.forEach(faceIndex => {
        const face = clippedFaces[faceIndex];
        const area = calculateFaceArea(face.vertices);
        totalArea += area;

        // 收集顶点
        face.vertices.forEach(vertex => {
          allVertices.push(vertex);
        });
      });

      // 确定大类
      let category = 'exterior';
      if (getNormalDirection(normal) === '上') {
        category = 'roof';
      } else if (getNormalDirection(normal) === '下') {
        category = 'ground';
      }

      const faceGroup: FaceGroup = {
        index: i,
        type: '裁剪面组',
        direction: getNormalDirection(normal),
        area: totalArea,
        perimeter: 0, // 临时值，后面会更新
        shapeCoefficient: 0, // 添加形状系数
        subFaceTypeCoefficient: 0, // 初始值为0，表示无门窗
        subFaceTotalArea: 0, // 初始值为0，表示无子面面积
        subFaceUValue: 0, // 初始值为0，表示无子面
        subFaceSHGC: 0, // 初始值为0，表示无子面
        conductivity: 1, // 导热系数默认为1
        thickness: 0.2, // 厚度默认为0.2
        longwaveAbsorptance: 0.9, // 长波辐射吸收比默认为0.9
        solarAbsorptance: 0.7, // 太阳辐射吸收比默认为0.7
        visibleAbsorptance: 0.7, // 可见光辐射吸收比默认为0.7
        vertexCount: allVertices.length,
        vertices: allVertices, // 使用所有顶点
        faceIndices: group,
        windows: [], // 初始化空的windows数组
        category: category, // 设置大类
        regionClass: 0, // 设置区域类默认值为0
        externalCondition: category === 'interior' ? 'Surface' : (category === 'roof' || category === 'exterior' ? 'Outdoors' : 'Ground') // 设置外接条件
      };

      // 计算并设置周长
      faceGroup.perimeter = calculateFaceGroupPerimeter(faceGroup);

      // 计算并设置形状系数
      faceGroup.shapeCoefficient = calculateShapeCoefficient(faceGroup.perimeter, faceGroup.area);

      faceGroups.value.push(faceGroup);
    }
  }

  console.log(`生成了 ${faceGroups.value.length} 个面组数据`);
};

// 渲染所有面组的门窗到3D视图
const renderAllWindowsTo3DView = () => {
  if (!scene) return;

  faceGroups.value.forEach(group => {
    if (group.windows && group.windows.length > 0) {
      group.windows.forEach(windowData => {
        renderWindowTo3DView(windowData, group);
      });
    }
  });
};

// 将门窗渲染到3D视图中
const renderWindowTo3DView = (windowData: any, faceGroup: FaceGroup) => {
  if (!scene || !faceGroup) return;

  // 获取面组的法向量
  let normal: THREE.Vector3;
  if (faceGroup.type === '交集面') {
    const faceIndex = faceGroup.faceIndices[0];
    normal = intersectionFaces[faceIndex].normal.clone();
  } else {
    const faceIndex = faceGroup.faceIndices[0];
    normal = clippedFaces[faceIndex].normal.clone();
  }

  // 计算面组的中心点
  const center = new THREE.Vector3();
  faceGroup.vertices.forEach(v => {
    (center as any).add(v);
  });
  (center as any).divideScalar(faceGroup.vertices.length);

  // 获取门窗在右上角视口中的位置
  const upperViewportPos = windowData.position.clone();

  // 计算反向变换的四元数
  const yAxis = new THREE.Vector3(0, 1, 0);
  const rotationAxis = new THREE.Vector3();
  (rotationAxis as any).crossVectors(normal, yAxis);

  let inverseQuaternion = new THREE.Quaternion();
  let angle = 0;
  if ((rotationAxis as any).length() > 0.001) {
    (rotationAxis as any).normalize();
    angle = Math.acos((normal as any).dot(yAxis));
    (inverseQuaternion as any).setFromAxisAngle(rotationAxis, -angle);
  }

  // 将右上角视口的2D位置转换回3D空间
  const localPos = new THREE.Vector3(upperViewportPos.x, 0, upperViewportPos.z);
  (localPos as any).applyQuaternion(inverseQuaternion);
  const worldPos = (localPos as any).add(center);

  // 创建门窗的3D几何体
  const geometry = new (THREE as any).PlaneGeometry(windowData.width, windowData.height);

  // 根据类型设置材质颜色
  const color = windowData.type === 'door' ? 0xff5555 : 0x4286f4;
  const material = new (THREE as any).MeshBasicMaterial({
    color: color,
    transparent: true,
    opacity: 0.8,
    side: (THREE as any).DoubleSide
  });

  // 创建网格
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.copy(worldPos);

  // 设置旋转，使门窗与面平行
  const defaultNormal = new THREE.Vector3(0, 0, 1);
  const targetNormal = normal.clone();
  (targetNormal as any).normalize();

  const windowRotationAxis = new THREE.Vector3();
  (windowRotationAxis as any).crossVectors(defaultNormal, targetNormal);

  const windowQuaternion = new THREE.Quaternion();
  if ((windowRotationAxis as any).length() > 0.001) {
    (windowRotationAxis as any).normalize();
    const windowAngle = Math.acos((defaultNormal as any).dot(targetNormal));
    (windowQuaternion as any).setFromAxisAngle(windowRotationAxis, windowAngle);
  }

  (mesh as any).quaternion.copy(windowQuaternion);

  // 对于南北朝向的面，需要额外绕X轴旋转90度
  if (Math.abs(targetNormal.x) > 0.9) {
    const additionalRotation = new THREE.Quaternion();
    (additionalRotation as any).setFromAxisAngle(new THREE.Vector3(0, 0, 1), Math.PI / 2);
    (mesh as any).quaternion.multiplyQuaternions(windowQuaternion, additionalRotation);
  }

  // 稍微向外偏移，避免z-fighting
  const offsetDirection = normal.clone().multiplyScalar(0.01);
  (mesh.position as any).add(offsetDirection);

  // 添加用户数据
  mesh.userData.isWindow3D = true;
  mesh.userData.windowData = windowData;
  mesh.userData.faceGroup = faceGroup;

  // 添加到主场景
  scene.add(mesh);
};

// 在右上视口平放并渲染面组
const renderFaceGroupInUpperViewport = (group: FaceGroup) => {
  if (!upperScene || !upperCamera) return;

  console.log('重新渲染面组:', group.index, '类型:', group.type);

  // 清除上方视口中的所有面对象和门窗对象
  upperScene.children = upperScene.children.filter(child => {
    const isFace = child.userData && child.userData.isFace;
    const isWindow = child.userData && child.userData.isWindow;
    if ((isFace || isWindow) && child instanceof THREE.Mesh) {
      if (child.geometry) {
        (child.geometry as any).dispose();
      }
      if (child.material) {
        if (Array.isArray(child.material)) {
          child.material.forEach(m => (m as any).dispose());
        } else {
          (child.material as any).dispose();
        }
      }
    }
    // 保留非面对象和非窗口对象（如网格和坐标轴）
    return !isFace && !isWindow;
  });

  // 清除主3D场景中该面组的所有门窗
  if (scene) {
    scene.children = scene.children.filter(child => {
      const isWindow3D = child.userData && child.userData.isWindow3D;
      if (isWindow3D && child.userData.faceGroup && child.userData.faceGroup.index === group.index) {
        if (child instanceof THREE.Mesh) {
          if (child.geometry) {
            (child.geometry as any).dispose();
          }
          if (child.material) {
            if (Array.isArray(child.material)) {
              child.material.forEach(m => (m as any).dispose());
            } else {
              (child.material as any).dispose();
            }
          }
        }
        return false;
      }
      return true;
    });
  }

  // 提取面的顶点和法向量
  let allVertices: THREE.Vector3[] = [];

  // 获取组内所有面的顶点
  if (group.type === '交集面') {
    // 对于交集面，直接使用其顶点
    const faceIndex = group.faceIndices[0];
    allVertices = intersectionFaces[faceIndex].vertices.map(v => v.clone());
  } else {
    // 对于裁剪面组，收集所有面的顶点
    group.faceIndices.forEach(faceIndex => {
      const face = clippedFaces[faceIndex];
      // 将每个裁剪面作为单独的四边形处理
      allVertices = allVertices.concat(face.vertices.map(v => v.clone()));
    });
  }

  // 获取组内第一个面，用于确定法向量
  let normal: THREE.Vector3;
  if (group.type === '交集面') {
    const faceIndex = group.faceIndices[0];
    normal = intersectionFaces[faceIndex].normal.clone();
  } else {
    const faceIndex = group.faceIndices[0];
    normal = clippedFaces[faceIndex].normal.clone();
  }

  // 如果没有顶点或法向量，返回
  if (allVertices.length < 3 || !normal) return;

  // 计算所有顶点的中心点（用于居中显示）
  const center = new THREE.Vector3();
  allVertices.forEach(v => {
    (center as any).add(v);
  });
  (center as any).divideScalar(allVertices.length);

  // 保存面组中心点，用于后续计算
  const groupCenter = center.clone();

  // 创建几何体
  const geometry = new THREE.BufferGeometry();
  const positions: number[] = [];

  if (group.type === '交集面') {
    // 对于交集面，判断顶点数量
    if (allVertices.length === 3) {
      // 三角形，直接使用
      positions.push(
        allVertices[0].x - center.x, allVertices[0].y - center.y, allVertices[0].z - center.z,
        allVertices[1].x - center.x, allVertices[1].y - center.y, allVertices[1].z - center.z,
        allVertices[2].x - center.x, allVertices[2].y - center.y, allVertices[2].z - center.z
      );
    } else if (allVertices.length === 4) {
      // 四边形，分解为两个三角形
      positions.push(
        allVertices[0].x - center.x, allVertices[0].y - center.y, allVertices[0].z - center.z,
        allVertices[1].x - center.x, allVertices[1].y - center.y, allVertices[1].z - center.z,
        allVertices[2].x - center.x, allVertices[2].y - center.y, allVertices[2].z - center.z,

        allVertices[0].x - center.x, allVertices[0].y - center.y, allVertices[0].z - center.z,
        allVertices[2].x - center.x, allVertices[2].y - center.y, allVertices[2].z - center.z,
        allVertices[3].x - center.x, allVertices[3].y - center.y, allVertices[3].z - center.z
      );
    } else if (allVertices.length > 4) {
      // 对于多于4个顶点的多边形，使用简单的三角形分解
      for (let i = 1; i < allVertices.length - 1; i++) {
        positions.push(
          allVertices[0].x - center.x, allVertices[0].y - center.y, allVertices[0].z - center.z,
          allVertices[i].x - center.x, allVertices[i].y - center.y, allVertices[i].z - center.z,
          allVertices[i+1].x - center.x, allVertices[i+1].y - center.y, allVertices[i+1].z - center.z
        );
      }
    }
  } else {
    // 对于裁剪面组，每四个顶点创建一个四边形
    for (let i = 0; i < allVertices.length; i += 4) {
      if (i + 3 < allVertices.length) {
        // 第一个三角形
        positions.push(
          allVertices[i].x - center.x, allVertices[i].y - center.y, allVertices[i].z - center.z,
          allVertices[i+1].x - center.x, allVertices[i+1].y - center.y, allVertices[i+1].z - center.z,
          allVertices[i+2].x - center.x, allVertices[i+2].y - center.y, allVertices[i+2].z - center.z
        );
        // 第二个三角形
        positions.push(
          allVertices[i].x - center.x, allVertices[i].y - center.y, allVertices[i].z - center.z,
          allVertices[i+2].x - center.x, allVertices[i+2].y - center.y, allVertices[i+2].z - center.z,
          allVertices[i+3].x - center.x, allVertices[i+3].y - center.y, allVertices[i+3].z - center.z
        );
      }
    }
  }

  // 设置顶点
  (geometry as any).setAttribute(
    'position',
    new (THREE as any).Float32BufferAttribute(positions, 3)
  );

  // 计算法向量
  (geometry as any).computeVertexNormals();

  // 创建材质
  const material = new THREE.MeshStandardMaterial({
    color: group.type === '交集面' ? 0xffff00 : 0x4286f4, // 交集面使用黄色，裁剪面使用蓝色
    transparent: false,
    opacity: 1.0
  });

  // 设置双面渲染
  (material as any).side = (THREE as any).DoubleSide;
  (material as any).flatShading = true;

  // 创建网格
  const mesh = new THREE.Mesh(geometry, material);
  mesh.userData.isFace = true;

  // 计算边界盒以确定缩放和位置
  geometry.computeBoundingBox();
  const size = new THREE.Vector3();
  (geometry.boundingBox as any).getSize(size);

  // 添加到场景
  upperScene.add(mesh);

  // 重置相机位置和旋转为俯视视角
  if (normal.z < -0.9) { // 如果面朝向-z方向
    upperCamera.position.set(0, 10, 0);
    (upperCamera as any).up.set(0, 0, 1); // 旋转180度
    upperCamera.lookAt(0, 0, 0);
  } else if (normal.x > 0.9) { // 如果面朝向+x方向
    upperCamera.position.set(0, 10, 0);
    (upperCamera as any).up.set(-1, 0, 0); // 顺时针旋转90度
    upperCamera.lookAt(0, 0, 0);
  } else if (normal.x < -0.9) { // 如果面朝向-x方向
    upperCamera.position.set(0, 10, 0);
    (upperCamera as any).up.set(1, 0, 0); // 逆时针旋转90度
    upperCamera.lookAt(0, 0, 0);
  } else {
    upperCamera.position.set(0, 10, 0);
    (upperCamera as any).up.set(0, 0, -1); // 默认方向
    upperCamera.lookAt(0, 0, 0);
  }
  upperCamera.updateProjectionMatrix();

  // 重置控制器目标点和更新
  upperOrbitControls.target.set(0, 0, 0);
  upperOrbitControls.update();

  // 旋转面使其平放（沿Y轴向上）
  // 计算从法向量到Y轴的旋转
  // 首先，找到法向量和Y轴的垂直轴
  const yAxis = new THREE.Vector3(0, 1, 0);
  const rotationAxis = new THREE.Vector3();
  (rotationAxis as any).crossVectors(normal, yAxis);

  if ((rotationAxis as any).length() > 0.001) {  // 如果不平行
    (rotationAxis as any).normalize();
    // 计算旋转角度
    const angle = Math.acos((normal as any).dot(yAxis));
    // 应用旋转
    const quaternion = new THREE.Quaternion();
    (quaternion as any).setFromAxisAngle(rotationAxis, angle);
    (mesh as any).quaternion.copy(quaternion);
  }

  // 更新控制器
  upperOrbitControls.update();

  // 确保group.windows数组已初始化
  if (!group.windows) {
    group.windows = [];
  }

  // 在OptView中渲染门窗到3D视图中的正确位置
  if (group.windows && group.windows.length > 0) {
    group.windows.forEach(windowData => {
      renderWindowTo3DView(windowData, group);
    });
  }

  // 在面组渲染完成后，渲染该面组关联的所有门窗
  if (group.windows && group.windows.length > 0) {
    console.log(`开始重新渲染 ${group.windows.length} 个门窗`);

    group.windows.forEach((windowData, index) => {
      // 创建平面几何体
      const geometry = new (THREE as any).PlaneGeometry(windowData.width, windowData.height);

      // 创建材质
      const material = new (THREE as any).MeshBasicMaterial({
        color: 0x4286f4, // 蓝色
        transparent: true,
        opacity: 0.9,
        side: (THREE as any).DoubleSide // 双面可见
      });

      // 创建网格
      const mesh = new THREE.Mesh(geometry, material);
      // 放置在xz平面上，需要旋转
      (mesh as any).rotation.x = -Math.PI / 2; // 旋转90度使其平躺在xz平面

      // 直接使用门窗的绝对位置
      mesh.position.copy(windowData.position);
      mesh.position.y = 0.02; // 稍微抬高一点，让门窗在面的上方

      // 如果原来有UUID，保留它，确保引用一致性
      if (windowData.mesh && (windowData.mesh as any).uuid) {
        (mesh as any).uuid = (windowData.mesh as any).uuid;
      }

      // 添加用户数据，标记为门窗
      mesh.userData.isWindow = true;
      mesh.userData.windowIndex = index; // 存储索引，方便查找

      // 添加顶点信息，用于创建选择边框
      const halfWidth = windowData.width / 2;
      const halfHeight = windowData.height / 2;
      mesh.userData.vertices = [
        new THREE.Vector3(windowData.position.x - halfWidth, 0.02, windowData.position.z - halfHeight),
        new THREE.Vector3(windowData.position.x + halfWidth, 0.02, windowData.position.z - halfHeight),
        new THREE.Vector3(windowData.position.x + halfWidth, 0.02, windowData.position.z + halfHeight),
        new THREE.Vector3(windowData.position.x - halfWidth, 0.02, windowData.position.z + halfHeight)
      ];

      // 更新windowData中的mesh引用
      windowData.mesh = mesh;

      // 添加到场景
      upperScene.add(mesh);

      console.log(`渲染门窗 ${index}，UUID: ${(mesh as any).uuid}`);
    });

    console.log(`完成渲染 ${group.windows.length} 个关联的门窗`);
  }
};

// 高亮显示选中的面组
const highlightGroup = (groupIndex: number) => {
  // 先清除当前选择
  clearSelection();

  // 检查是否是有效的组索引
  if (groupIndex < 0 || groupIndex >= faceGroups.value.length) {
    console.error(`无效的面组索引: ${groupIndex}`);
    return;
  }

  const group = faceGroups.value[groupIndex];
  // 设置当前选中组索引
  currentSelectedGroupIndex.value = groupIndex;

  if (group.type === '交集面') {
    // 高亮显示交集面
    const faceIndex = group.faceIndices[0];
    const mesh = intersectionFaceMeshes[faceIndex];

    if (mesh) {
      // 切换到交集面显示模式
      showIntersections.value = true;
      showClippedFaces.value = false;
      updateFacesVisibility();

      // 设置为选中状态
      selectedFace = mesh;

      // 保存原始颜色
      if (mesh.material instanceof THREE.MeshStandardMaterial) {
        originalColors.set(mesh, (mesh.material.color as any).getHex());
        (mesh.material.color as any).setHex(SELECTED_COLOR);
      }

      // 创建边框
      selectionBorder = createSelectionBorder(mesh);

      // 更新选中面信息
      const face = intersectionFaces[faceIndex];
      const parentFacesInfo = face.parentFaces?.map((parentIndex: number) => {
        const parentCubeIndex = Math.floor(parentIndex / 6);
        const parentFace = allCubeFaces[parentIndex];
        return {
          index: parentIndex,
          cubeIndex: parentCubeIndex,
          direction: getNormalDirection(parentFace.normal)
        };
      });

      selectedFaceInfo.value = {
        index: faceIndex,
        direction: '内墙',
        normal: `(${face.normal.x}, ${face.normal.y}, ${face.normal.z})`,
        vertexCount: face.vertices.length,
        cubeIndex: -1,
        area: calculateFaceArea(face.vertices),
        isIntersection: true,
        parentFaces: parentFacesInfo
      };

      // 在右上视口平放并渲染该面组
      renderFaceGroupInUpperViewport(group);
    }
  } else if (group.type === '裁剪面组') {
    // 高亮显示裁剪面组
    // 切换到裁剪面显示模式
    showIntersections.value = false;
    showClippedFaces.value = true;
    updateFacesVisibility();

    // 获取组内第一个面作为选中面
    const faceIndex = group.faceIndices[0];
    const mesh = clippedFaceMeshes[faceIndex];

    if (mesh) {
      // 设置为选中状态
      selectedFace = mesh;

      // 保存原始颜色
      if (mesh.material instanceof THREE.MeshStandardMaterial) {
        originalColors.set(mesh, (mesh.material.color as any).getHex());
        (mesh.material.color as any).setHex(SELECTED_COLOR);
      }

      // 创建边框
      selectionBorder = createSelectionBorder(mesh);

      // 高亮显示同组的所有面
      group.faceIndices.forEach(idx => {
        if (idx !== faceIndex) {
          const groupMesh = clippedFaceMeshes[idx];
          if (groupMesh && groupMesh.material instanceof THREE.MeshStandardMaterial) {
            // 保存原始颜色
            if (!originalColors.has(groupMesh)) {
              originalColors.set(groupMesh, (groupMesh.material.color as any).getHex());
            }
            // 设置为浅蓝色
            (groupMesh.material.color as any).setHex(0xaaddff);

            // 为同组面创建红色边框
            const border = createSelectionBorder(groupMesh);
            if (border) {
              groupSelectionBorders.push(border);
            }
          }
        }
      });

      // 更新选中面信息
      const face = clippedFaces[faceIndex];
      const parentFace = face.parentFace !== undefined ? allCubeFaces[face.parentFace] : undefined;
      const parentFaceInfo = parentFace && face.parentFace !== undefined ? {
        index: face.parentFace,
        cubeIndex: Math.floor(face.parentFace / 6),
        direction: getNormalDirection(parentFace.normal)
      } : undefined;

      selectedFaceInfo.value = {
        index: faceIndex,
        direction: getNormalDirection(face.normal),
        normal: `(${face.normal.x}, ${face.normal.y}, ${face.normal.z})`,
        vertexCount: face.vertices.length,
        cubeIndex: parentFaceInfo ? parentFaceInfo.cubeIndex : -1,
        area: calculateFaceArea(face.vertices),
        isIntersection: false,
        isClipped: true,
        parentFace: parentFaceInfo
      };

      // 在右上视口平放并渲染该面组
      renderFaceGroupInUpperViewport(group);
    }
  }
};

// 计算向量叉积
const crossProduct = (v1: number[], v2: number[]): number[] => {
  return [
    v1[1] * v2[2] - v1[2] * v2[1], // x
    v1[2] * v2[0] - v1[0] * v2[2], // y
    v1[0] * v2[1] - v1[1] * v2[0]  // z
  ];
};

// 计算向量大小
const vectorMagnitude = (v: number[]): number => {
  return Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]);
};

// 计算向量点积
const dotProduct = (v1: number[], v2: number[]): number => {
  return v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2];
};

// 从两点计算向量
const vectorFromPoints = (p1: number[], p2: number[]): number[] => {
  return [p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]];
};

// 判断点是否在线段上
const isPointOnLine = (point: number[], lineStart: number[], lineEnd: number[], tolerance: number = 1e-6): boolean => {
  const lineVec = vectorFromPoints(lineStart, lineEnd);
  const pointVec = vectorFromPoints(lineStart, point);
  const crossProd = crossProduct(lineVec, pointVec);

  // 如果叉积不接近零，点不在直线上
  if (vectorMagnitude(crossProd) > tolerance) {
    return false;
  }

  // 检查点是否在线段上（而不仅仅是直线上）
  const dotProd = dotProduct(pointVec, lineVec);
  const lineMagSquared = dotProduct(lineVec, lineVec);

  // 如果点积小于0或大于线段长度的平方，点不在线段上
  if (dotProd < -tolerance || dotProd > lineMagSquared + tolerance) {
    return false;
  }

  return true;
};

// 检查两个多边形是否有边-边连接
const checkEdgeEdgeConnection = (polygon1: number[][], polygon2: number[][]): boolean => {
  // 生成多边形1的所有边
  const edges1 = [];
  for (let i = 0; i < polygon1.length; i++) {
    edges1.push([polygon1[i], polygon1[(i + 1) % polygon1.length]]);
  }

  // 生成多边形2的所有边
  const edges2 = [];
  for (let i = 0; i < polygon2.length; i++) {
    edges2.push([polygon2[i], polygon2[(i + 1) % polygon2.length]]);
  }

  // 检查每对边是否有连接
  for (const edge1 of edges1) {
    for (const edge2 of edges2) {
      // 检查edge1的端点是否在edge2上
      if (isPointOnLine(edge1[0], edge2[0], edge2[1]) ||
          isPointOnLine(edge1[1], edge2[0], edge2[1])) {
        return true;
      }

      // 检查edge2的端点是否在edge1上
      if (isPointOnLine(edge2[0], edge1[0], edge1[1]) ||
          isPointOnLine(edge2[1], edge1[0], edge1[1])) {
        return true;
      }
    }
  }

  return false;
};

// 将THREE.Vector3转换为简单数组
const vector3ToArray = (v: THREE.Vector3): number[] => {
  return [v.x, v.y, v.z];
};

// 计算面组之间的邻接矩阵
const calculateAdjacencyMatrix = () => {
  const n = faceGroups.value.length;
  const matrix: number[][] = Array(n).fill(0).map(() => Array(n).fill(0));

  // 对角线元素设为1（自己与自己相邻）
  for (let i = 0; i < n; i++) {
    matrix[i][i] = 1;
  }

  // 两两比较面组
  for (let i = 0; i < n; i++) {
    for (let j = i + 1; j < n; j++) {
      const group1 = faceGroups.value[i];
      const group2 = faceGroups.value[j];

      // 将THREE.Vector3转换为简单数组
      const vertices1 = group1.vertices.map(vector3ToArray);
      const vertices2 = group2.vertices.map(vector3ToArray);

      // 检查是否有边-边连接
      const isConnected = checkEdgeEdgeConnection(vertices1, vertices2);

      // 更新邻接矩阵（对称）
      matrix[i][j] = isConnected ? 1 : 0;
      matrix[j][i] = matrix[i][j];
    }
  }

  adjacencyMatrix.value = matrix;
  console.log('计算了邻接矩阵:', matrix);
};

// 切换邻接矩阵弹窗显示
const toggleAdjacencyMatrixDialog = () => {
  if (!showAdjacencyMatrixDialog.value && adjacencyMatrix.value.length === 0) {
    // 首次显示时计算邻接矩阵
    calculateAdjacencyMatrix();
  }
  showAdjacencyMatrixDialog.value = true;
};

// 关闭邻接矩阵弹窗
const closeAdjacencyMatrixDialog = () => {
  showAdjacencyMatrixDialog.value = false;
};

// 初始化右上角视口场景
const initUpperScene = () => {
  if (!upperCanvasRef.value) return;

  upperScene = new THREE.Scene();
  upperScene.background = new THREE.Color(0xf0f0f0);

  // 创建相机 - 固定在(0,10,0)位置
  upperCamera = new THREE.PerspectiveCamera(
    75,
    upperCanvasRef.value.clientWidth / upperCanvasRef.value.clientHeight,
    0.1,
    1000
  );
  upperCamera.position.set(0, 10, 0);
  upperCamera.lookAt(0, 0, 0);

  // 创建渲染器
  upperRenderer = new THREE.WebGLRenderer({
    canvas: upperCanvasRef.value,
    antialias: true,
  });
  upperRenderer.setSize(
    upperCanvasRef.value.clientWidth,
    upperCanvasRef.value.clientHeight
  );
  upperRenderer.setPixelRatio(window.devicePixelRatio);

  // 添加轨道控制器
  upperOrbitControls = new OrbitControls(upperCamera, upperRenderer.domElement);
  upperOrbitControls.enableDamping = true;

  // 设置控制方式 - 中键平移，禁用右键旋转
  upperOrbitControls.mouseButtons = {
    LEFT: null,   // 左键不做任何操作
    MIDDLE: 2,    // 中键平移 (2 = PAN)
    RIGHT: null   // 禁用右键旋转
  };

  // 添加网格和坐标轴
  const gridHelper = new THREE.GridHelper(10, 10);
  upperScene.add(gridHelper);

  const axesHelper = new THREE.AxesHelper(5);
  upperScene.add(axesHelper);

  // 添加光源
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  upperScene.add(ambientLight);

  const directionalLight = new THREE.DirectionalLight(0xffffff, 0.6);
  directionalLight.position.set(10, 20, 15);
  upperScene.add(directionalLight);
};

// 添加当前选中组索引变量
const currentSelectedGroupIndex = ref<number | null>(null);
// 添加侧边栏展开状态变量
const isSidebarExpanded = ref(true);
// 添加绘制门窗按钮状态
const isDrawingEnabled = ref(false);
// 添加绘制相关状态
const isDrawing = ref(false);
const drawStartPosition = ref<THREE.Vector2 | null>(null);
const currentRectMesh = ref<THREE.Mesh | null>(null);

// 添加门窗矩形选中变量
const selectedWindowMesh = ref<THREE.Mesh | null>(null);
let windowSelectionBorder: THREE.LineSegments | null = null;

// 添加绘制门窗相关的事件处理函数
// 添加绘制门窗相关的事件处理
const initDrawingEvents = () => {
  if (!upperCanvasRef.value) return;

  // 添加鼠标事件监听
  upperCanvasRef.value.addEventListener('mousedown', handleDrawMouseDown);
  upperCanvasRef.value.addEventListener('mousemove', handleDrawMouseMove);
  upperCanvasRef.value.addEventListener('mouseup', handleDrawMouseUp);

  // 添加鼠标点击事件监听
  upperCanvasRef.value.addEventListener('click', onUpperCanvasClick);

  // 监听绘制模式状态变化
  watch(isDrawingEnabled, (newValue) => {
    // 清除绘制状态
    if (!newValue) {
      clearDrawing();
    }
  });
};

// 处理鼠标按下事件
const handleDrawMouseDown = (event: MouseEvent) => {
  if (!isDrawingEnabled.value || !upperScene || !upperCamera || !upperCanvasRef.value) return;

  // 获取鼠标在canvas中的位置
  const rect = upperCanvasRef.value.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  // 将鼠标位置从屏幕空间转换为3D空间中的点
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(new THREE.Vector2(x, y), upperCamera);

  // 创建一个平面，使其与相机方向垂直且y=0
  const plane = new (THREE as any).Plane(new THREE.Vector3(0, 1, 0), 0);

  // 计算射线与平面的交点
  const intersection = new THREE.Vector3();
  (raycaster as any).ray.intersectPlane(plane, intersection);

  // 保存起始位置
  drawStartPosition.value = new THREE.Vector2(intersection.x, intersection.z);

  // 开始绘制
  isDrawing.value = true;

  // 创建初始矩形
  createDrawingRect(
    intersection.x, 0, intersection.z,
    0.1, 0.1 // 最小尺寸
  );
};

// 处理鼠标移动事件
const handleDrawMouseMove = (event: MouseEvent) => {
  if (!isDrawingEnabled.value || !isDrawing.value || !drawStartPosition.value || !upperCanvasRef.value) return;

  // 获取鼠标在canvas中的位置
  const rect = upperCanvasRef.value.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  // 计算当前位置
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(new THREE.Vector2(x, y), upperCamera);

  // 创建一个y=0平面
  const plane = new (THREE as any).Plane(new THREE.Vector3(0, 1, 0), 0);

  // 计算射线与平面的交点
  const intersection = new THREE.Vector3();
  if ((raycaster as any).ray.intersectPlane(plane, intersection)) {
    const currentPos = new THREE.Vector2(intersection.x, intersection.z);

    // 更新矩形
    updateDrawingRect(drawStartPosition.value, currentPos);
  }
};

// 处理鼠标释放事件
const handleDrawMouseUp = () => {
  if (!isDrawingEnabled.value || !isDrawing.value) return;

  // 完成绘制
  isDrawing.value = false;

  // 保留绘制的矩形
  finalizeDrawingRect();

  // 为门窗添加用户数据，标记为可选择的门窗
  if (currentRectMesh.value) {
    currentRectMesh.value.userData.isWindow = true;
  }

  // 清除绘制状态，但保留绘制的结果
  drawStartPosition.value = null;

  // 退出绘制模式
  isDrawingEnabled.value = false;
};

// 创建绘制矩形
const createDrawingRect = (x: number, y: number, z: number, width: number, depth: number) => {
  if (!upperScene) return;

  // 如果已有绘制中的矩形，先移除
  if (currentRectMesh.value && upperScene) {
    upperScene.remove(currentRectMesh.value);
  }

  // 创建平面几何体 - 长方形在xz平面上，y=0
  const geometry = new (THREE as any).PlaneGeometry(width, depth);

  // 创建材质
  const material = new (THREE as any).MeshBasicMaterial({
    color: 0xff4444, // 红色
    transparent: true,
    opacity: 0.7,
    side: (THREE as any).DoubleSide // 双面可见
  });

  // 创建网格
  const mesh = new THREE.Mesh(geometry, material);
  // 放置在xz平面上，需要旋转
  (mesh as any).rotation.x = -Math.PI / 2; // 旋转90度使其平躺在xz平面
  mesh.position.set(x + width/2, 0.01, z + depth/2); // 稍微抬高一点避免z-fighting

  // 添加到场景
  upperScene.add(mesh);

  // 保存当前矩形
  currentRectMesh.value = mesh;
};

// 更新绘制矩形
const updateDrawingRect = (startPos: THREE.Vector2, currentPos: THREE.Vector2) => {
  if (!currentRectMesh.value || !upperScene) return;

  // 计算宽度和深度
  const width = Math.abs(currentPos.x - startPos.x);
  const depth = Math.abs(currentPos.y - startPos.y);

  // 计算中心点
  const centerX = (startPos.x + currentPos.x) / 2;
  const centerZ = (startPos.y + currentPos.y) / 2;

  // 更新几何体
  if (currentRectMesh.value && currentRectMesh.value.geometry) {
    // 释放之前的几何体
    (currentRectMesh.value.geometry as any).dispose();

    // 创建新的几何体
    const geometry = new (THREE as any).PlaneGeometry(width, depth);

    // 替换几何体
    currentRectMesh.value.geometry = geometry;
  }

  // 更新位置
  currentRectMesh.value.position.set(centerX, 0.01, centerZ);
};

// 完成绘制矩形
const finalizeDrawingRect = () => {
  // 只有在实际拖动创建了矩形后才进行处理
  if (currentRectMesh.value &&
      (currentRectMesh.value.geometry as any) instanceof (THREE as any).PlaneGeometry &&
      currentRectMesh.value.material instanceof (THREE as any).MeshBasicMaterial) {

    // 获取矩形尺寸
    const width = (currentRectMesh.value.geometry as any).parameters?.width || 0;
    const height = (currentRectMesh.value.geometry as any).parameters?.height || 0;

    // 检查尺寸是否太小
    if (width < 0.1 || height < 0.1) {
      // 尺寸太小，移除
      if (upperScene) {
        upperScene.remove(currentRectMesh.value);
        currentRectMesh.value = null;
      }
      return;
    }

    // 根据当前类型设置颜色
    const type = editingWindowInfo.value.type;
    const color = type === 'door' ? 0xff5555 : 0x4286f4; // 门为红色，窗为蓝色

    // 改变材质颜色
    (currentRectMesh.value.material as any).color.set(color);
    (currentRectMesh.value.material as any).opacity = 0.9;

    // 将门窗添加到当前选中的面组
    if (currentSelectedGroupIndex.value !== null && faceGroups.value[currentSelectedGroupIndex.value]) {
      const windowData = {
        position: currentRectMesh.value.position.clone(),
        width: width,
        height: height,
        type: type, // 使用当前类型
        uValue: 1.5, // 添加默认U值
        shgc: type === 'window' ? 0.5 : 0, // 添加默认SHGC值，窗户为0.5，门为0
        mesh: currentRectMesh.value
      };

      // 将门窗添加到面组的windows数组中
      faceGroups.value[currentSelectedGroupIndex.value].windows.push(windowData);

      // 更新子面类型系数
      faceGroups.value[currentSelectedGroupIndex.value].subFaceTypeCoefficient = calculateSubFaceTypeCoefficient(faceGroups.value[currentSelectedGroupIndex.value].windows);

      // 更新子面总面积
      faceGroups.value[currentSelectedGroupIndex.value].subFaceTotalArea = calculateSubFaceTotalArea(faceGroups.value[currentSelectedGroupIndex.value].windows);

      // 更新子面U值
      faceGroups.value[currentSelectedGroupIndex.value].subFaceUValue = calculateSubFaceUValue(faceGroups.value[currentSelectedGroupIndex.value].windows);

      // 更新子面SHGC值
      faceGroups.value[currentSelectedGroupIndex.value].subFaceSHGC = calculateSubFaceSHGC(faceGroups.value[currentSelectedGroupIndex.value].windows);

      // 记录门窗数据
      console.log('添加门窗到面组:', currentSelectedGroupIndex.value + 1, windowData);
    } else {
      console.warn('未选中面组，无法关联门窗');
    }
  }
};

// 清除绘制状态
const clearDrawing = () => {
  isDrawing.value = false;
  drawStartPosition.value = null;

  // 如果只是取消当前绘制而不是完成绘制，则移除矩形
  if (isDrawing.value && currentRectMesh.value && upperScene) {
    upperScene.remove(currentRectMesh.value);
    currentRectMesh.value = null;
  }
};

// 修改onUpperCanvasClick函数，让信息栏位置固定在点击位置
const onUpperCanvasClick = (event: MouseEvent) => {
  if (!upperCanvasRef.value || !upperScene || !upperCamera) return;

  // 如果正在绘制，则不处理点击事件
  if (isDrawingEnabled.value) return;

  // 计算鼠标在画布中的位置
  const rect = upperCanvasRef.value.getBoundingClientRect();
  const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  // 设置射线投射器
  const raycaster = new THREE.Raycaster();
  raycaster.setFromCamera(new THREE.Vector2(x, y), upperCamera);

  // 获取场景中的所有门窗对象
  const windowObjects = upperScene.children.filter(child =>
    child instanceof THREE.Mesh && child.userData && child.userData.isWindow
  );

  // 获取与射线相交的对象
  const intersects = raycaster.intersectObjects(windowObjects, false);

  // 隐藏门窗信息提示
  showWindowInfoTooltip.value = false;
  selectedWindowInfo.value = null;

  // 清除之前的选择
  if (selectedWindowMesh.value) {
    // 恢复之前选中的门窗的原始颜色
    if (selectedWindowMesh.value.material instanceof THREE.MeshBasicMaterial) {
      (selectedWindowMesh.value.material as any).color.set(0x4286f4); // 蓝色
      (selectedWindowMesh.value.material as any).opacity = 0.9;
    }
  }

  // 移除之前的边框
  if (windowSelectionBorder && upperScene) {
    upperScene.remove(windowSelectionBorder);
    windowSelectionBorder = null;
  }

  // 如果有相交的对象
  if (intersects.length > 0) {
    const mesh = intersects[0].object as THREE.Mesh;

    // 设置新的选中对象
    selectedWindowMesh.value = mesh;

    // 高亮显示选中的门窗
    if (mesh.material instanceof THREE.MeshBasicMaterial) {
      (mesh.material as any).color.set(0xff4444); // 红色
      (mesh.material as any).opacity = 1.0;
    }

    // 创建选择边框 - 重用下方视图的createSelectionBorder函数
    // 首先需要为门窗添加顶点信息
    if (!mesh.userData.vertices) {
      // 使用几何体的尺寸和位置创建顶点数据
      const geometry = mesh.geometry as any;
      if (geometry && geometry.parameters) {
        const width = geometry.parameters.width;
        const height = geometry.parameters.height;
        const position = mesh.position;

        // 创建平面顶点（考虑到旋转）
        mesh.userData.vertices = [
          new THREE.Vector3(position.x - width/2, 0.01, position.z - height/2),
          new THREE.Vector3(position.x + width/2, 0.01, position.z - height/2),
          new THREE.Vector3(position.x + width/2, 0.01, position.z + height/2),
          new THREE.Vector3(position.x - width/2, 0.01, position.z + height/2)
        ];
      }
    }

    // 创建选择边框
    if (mesh.userData.vertices) {
      windowSelectionBorder = createSelectionBorder(mesh, 0xff0000, upperScene);
    }

    // 查找当前选中门窗对应的窗口数据
    if (currentSelectedGroupIndex.value !== null) {
      const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
      const windowData = currentGroup.windows.find(w =>
        w.mesh && (w.mesh as any).uuid === (mesh as any).uuid
      );

      // 获取门窗信息
      const geometry = mesh.geometry as any;
      if (geometry && geometry.parameters) {
        const width = geometry.parameters.width;
        const height = geometry.parameters.height;
        const area = width * height;

        // 获取类型，如果找到了对应的窗口数据则使用其类型，否则默认为'window'
        const type = windowData?.type || 'window';

        // 获取U值，如果找到了对应的窗口数据则使用其U值，否则默认为1.5
        const uValue = windowData?.uValue || 1.5;

        // 获取SHGC值，根据窗口类型设置默认值
        let shgc = windowData?.shgc ?? (type === 'window' ? 0.5 : 0);

        // 更新选中门窗信息
        selectedWindowInfo.value = {
          width,
          height,
          area,
          type,
          uValue,
          shgc
        };

        // 初始化编辑窗口信息，使用找到的门窗实际类型
        editingWindowInfo.value = {
          width: width,
          height: height,
          type: type,
          uValue: uValue,
          shgc: shgc
        };

        // 设置信息提示位置为鼠标点击位置附近，不随鼠标移动变化
        windowInfoPosition.value = {
          x: event.clientX + 10, // 向右偏移10像素
          y: event.clientY - 10  // 向上偏移10像素
        };

        // 显示信息提示
        showWindowInfoTooltip.value = true;
      }
    }

    console.log('选中了门窗:', mesh);
  } else {
    // 没有选中任何对象
    selectedWindowMesh.value = null;
  }
};

// 添加门窗信息显示相关的变量
const showWindowInfoTooltip = ref(false);
const windowInfoPosition = ref({ x: 0, y: 0 });
const selectedWindowInfo = ref<{
  width: number;
  height: number;
  area: number;
  type: string; // 添加类型字段
  uValue: number; // 添加U值字段
  shgc: number; // 添加SHGC值字段
} | null>(null);

// 添加窗口删除函数，修复删除功能
const deleteSelectedWindow = () => {
  // 确保有选中的门窗和当前选中的面组
  if (!selectedWindowMesh.value || currentSelectedGroupIndex.value === null) {
    console.warn('无法删除门窗: 未选中门窗或面组');
    return;
  }

  // 获取当前面组
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  if (!currentGroup || !currentGroup.windows) {
    console.warn('无法删除门窗: 当前面组无效或没有windows数组');
    return;
  }

  console.log('尝试删除门窗，当前面组windows数量:', currentGroup.windows.length);
  console.log('选中的门窗对象ID:', (selectedWindowMesh.value as any).uuid);

  // 找到要删除的门窗索引 - 使用uuid比较更可靠
  const windowIndex = currentGroup.windows.findIndex(windowData =>
    windowData.mesh && (windowData.mesh as any).uuid === (selectedWindowMesh.value as any)?.uuid
  );

  console.log('找到的门窗索引:', windowIndex);

  // 如果找到了对应的门窗
  if (windowIndex !== -1) {
    // 从场景中删除门窗
    if (upperScene && selectedWindowMesh.value) {
      upperScene.remove(selectedWindowMesh.value);

      // 如果有边框，也一并删除
      if (windowSelectionBorder) {
        upperScene.remove(windowSelectionBorder);
        windowSelectionBorder = null;
      }

      console.log('已从场景中移除门窗对象');
    }

    // 从面组的windows数组中删除
    const removedWindow = currentGroup.windows.splice(windowIndex, 1)[0];
    console.log('已从面组数组中移除门窗数据:', removedWindow);

    // 更新子面类型系数
    currentGroup.subFaceTypeCoefficient = calculateSubFaceTypeCoefficient(currentGroup.windows);

    // 更新子面总面积
    currentGroup.subFaceTotalArea = calculateSubFaceTotalArea(currentGroup.windows);

    // 更新子面U值
    currentGroup.subFaceUValue = calculateSubFaceUValue(currentGroup.windows);

    // 更新子面SHGC值
    currentGroup.subFaceSHGC = calculateSubFaceSHGC(currentGroup.windows);

    // 清除选中状态
    selectedWindowMesh.value = null;

    // 隐藏信息提示
    showWindowInfoTooltip.value = false;
    selectedWindowInfo.value = null;

    console.log(`从面组 ${currentSelectedGroupIndex.value + 1} 中删除了门窗，剩余门窗数量:`, currentGroup.windows.length);

    // 强制更新面组数据以确保视图更新
    faceGroups.value = [...faceGroups.value];

    // 关键修复：重新渲染当前面组以立即刷新视图
    renderFaceGroupInUpperViewport(currentGroup);
  } else {
    console.warn('未找到要删除的门窗');

    // 打印所有门窗UUID以便调试
    console.log('当前面组中所有门窗的UUID:');
    currentGroup.windows.forEach((win, idx) => {
      console.log(`门窗 ${idx}:`, win.mesh ? (win.mesh as any).uuid : 'null');
    });
  }
};

// 添加门窗信息显示相关的变量
const editingWindowInfo = ref({ width: 0, height: 0, type: 'window', uValue: 1.5, shgc: 0.5 });

// 添加保存窗口尺寸的函数
const saveWindowDimensions = () => {
  // 验证输入的尺寸
  const width = parseFloat(editingWindowInfo.value.width.toString());
  const height = parseFloat(editingWindowInfo.value.height.toString());

  if (isNaN(width) || width <= 0 || isNaN(height) || height <= 0) {
    console.error('门窗尺寸无效，请输入正数');
    return;
  }

  if (!selectedWindowMesh.value || currentSelectedGroupIndex.value === null) {
    console.error('未选中门窗或面组');
    return;
  }

  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];

  // 查找选中的门窗对象在当前面组的索引
  const windowIndex = currentGroup.windows.findIndex(windowData =>
    windowData.mesh && (windowData.mesh as any).uuid === (selectedWindowMesh.value as any)?.uuid
  );

  if (windowIndex !== -1) {
    const windowData = currentGroup.windows[windowIndex];

    // 更新窗口数据
    windowData.width = width;
    windowData.height = height;
    windowData.type = editingWindowInfo.value.type; // 更新类型
    windowData.uValue = editingWindowInfo.value.uValue; // 更新U值

    // 如果是窗户类型，使用编辑值，如果是门，固定为0
    windowData.shgc = editingWindowInfo.value.type === 'window' ? editingWindowInfo.value.shgc : 0;

    // 更新窗口网格
    if (selectedWindowMesh.value && upperScene) {
      // 移除旧的网格
      upperScene.remove(selectedWindowMesh.value);

      // 创建新的几何体
      const geometry = new (THREE as any).PlaneGeometry(width, height);

      // 创建材质
      const material = new (THREE as any).MeshBasicMaterial({
        color: 0x4286f4, // 蓝色
        transparent: true,
        opacity: 0.9,
        side: (THREE as any).DoubleSide // 双面可见
      });

      // 创建新的网格
      const mesh = new THREE.Mesh(geometry, material);
      (mesh as any).rotation.x = -Math.PI / 2; // 旋转90度使其平躺在xz平面

      // 使用原来的位置
      mesh.position.copy(windowData.position);
      mesh.position.y = 0.02; // 稍微抬高一点，让门窗在面的上方

      // 保留原来的UUID，确保引用一致性
      (mesh as any).uuid = (selectedWindowMesh.value as any).uuid;

      // 添加用户数据，标记为门窗
      mesh.userData.isWindow = true;
      mesh.userData.windowIndex = windowIndex;

      // 更新顶点信息
      const halfWidth = width / 2;
      const halfHeight = height / 2;
      mesh.userData.vertices = [
        new THREE.Vector3(windowData.position.x - halfWidth, 0.02, windowData.position.z - halfHeight),
        new THREE.Vector3(windowData.position.x + halfWidth, 0.02, windowData.position.z - halfHeight),
        new THREE.Vector3(windowData.position.x + halfWidth, 0.02, windowData.position.z + halfHeight),
        new THREE.Vector3(windowData.position.x - halfWidth, 0.02, windowData.position.z + halfHeight)
      ];

      // 更新windowData中的mesh引用
      windowData.mesh = mesh;

      // 添加到场景
      upperScene.add(mesh);

      // 更新选中的mesh
      selectedWindowMesh.value = mesh;

      // 使用 requestAnimationFrame 确保场景被重新渲染
      requestAnimationFrame(() => {
        upperRenderer.render(upperScene, upperCamera);
      });

      console.log('更新了门窗尺寸:', width, height);
    }

    // 强制更新面组数据以确保视图更新
    faceGroups.value = [...faceGroups.value];

    // 更新选中窗口信息
    selectedWindowInfo.value = {
      width,
      height,
      area: width * height,
      type: editingWindowInfo.value.type,
      uValue: editingWindowInfo.value.uValue,
      shgc: editingWindowInfo.value.type === 'window' ? editingWindowInfo.value.shgc : 0
    };

    // 调用 renderFaceGroupInUpperViewport 重新渲染当前面组
    renderFaceGroupInUpperViewport(currentGroup);

    console.log('保存门窗尺寸成功');
  } else {
    console.error('未找到要更新的门窗');
  }
};

// 更新窗口尺寸
const updateWindowDimensions = () => {
  // 验证输入的尺寸
  const width = parseFloat(editingWindowInfo.value.width.toString());
  const height = parseFloat(editingWindowInfo.value.height.toString());

  if (isNaN(width) || width <= 0 || isNaN(height) || height <= 0) {
    console.error('门窗尺寸无效，请输入正数');
    return;
  }

  if (!selectedWindowMesh.value || currentSelectedGroupIndex.value === null) {
    console.error('未选中门窗或面组');
    return;
  }

  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];

  // 查找选中的门窗对象在当前面组的索引
  const windowIndex = currentGroup.windows.findIndex(windowData =>
    windowData.mesh && (windowData.mesh as any).uuid === (selectedWindowMesh.value as any)?.uuid
  );

  if (windowIndex !== -1) {
    const windowData = currentGroup.windows[windowIndex];

    // 更新窗口数据
    windowData.width = width;
    windowData.height = height;
    windowData.type = editingWindowInfo.value.type; // 更新类型
    windowData.uValue = editingWindowInfo.value.uValue; // 更新U值

    // 如果是窗户类型，使用编辑值，如果是门，固定为0
    windowData.shgc = editingWindowInfo.value.type === 'window' ? editingWindowInfo.value.shgc : 0;

    // 更新子面总面积 - 将更新移到这里，确保在每次修改尺寸时都会更新
    currentGroup.subFaceTotalArea = calculateSubFaceTotalArea(currentGroup.windows);

    // 更新子面U值
    currentGroup.subFaceUValue = calculateSubFaceUValue(currentGroup.windows);

    // 更新子面SHGC值
    currentGroup.subFaceSHGC = calculateSubFaceSHGC(currentGroup.windows);

    // 更新窗口网格
    if (selectedWindowMesh.value && upperScene) {
      // 移除旧的网格
      upperScene.remove(selectedWindowMesh.value);

      // 创建新的几何体
      const geometry = new (THREE as any).PlaneGeometry(width, height);

      // 根据类型选择颜色
      const type = editingWindowInfo.value.type;
      const color = type === 'door' ? 0xff5555 : 0x4286f4; // 门为红色，窗为蓝色

      // 创建材质
      const material = new (THREE as any).MeshBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.9,
        side: (THREE as any).DoubleSide // 双面可见
      });

      // 创建新的网格
      const mesh = new THREE.Mesh(geometry, material);
      (mesh as any).rotation.x = -Math.PI / 2; // 旋转90度使其平躺在xz平面

      // 使用原来的位置
      mesh.position.copy(windowData.position);
      mesh.position.y = 0.02; // 稍微抬高一点，让门窗在面的上方

      // 保留原来的UUID，确保引用一致性
      (mesh as any).uuid = (selectedWindowMesh.value as any).uuid;

      // 添加用户数据，标记为门窗
      mesh.userData.isWindow = true;
      mesh.userData.windowIndex = windowIndex;

      // 更新顶点信息
      const halfWidth = width / 2;
      const halfHeight = height / 2;
      mesh.userData.vertices = [
        new THREE.Vector3(windowData.position.x - halfWidth, 0.02, windowData.position.z - halfHeight),
        new THREE.Vector3(windowData.position.x + halfWidth, 0.02, windowData.position.z - halfHeight),
        new THREE.Vector3(windowData.position.x + halfWidth, 0.02, windowData.position.z + halfHeight),
        new THREE.Vector3(windowData.position.x - halfWidth, 0.02, windowData.position.z + halfHeight)
      ];

      // 更新windowData中的mesh引用
      windowData.mesh = mesh;

      // 添加到场景
      upperScene.add(mesh);

      // 更新选中的mesh
      selectedWindowMesh.value = mesh;

      // 使用 requestAnimationFrame 确保场景被重新渲染
      requestAnimationFrame(() => {
        upperRenderer.render(upperScene, upperCamera);
      });

      console.log('更新了门窗尺寸:', width, height);
    }

    // 强制更新面组数据以确保视图更新
    faceGroups.value = [...faceGroups.value];

    // 更新选中窗口信息
    selectedWindowInfo.value = {
      width,
      height,
      area: width * height,
      type: editingWindowInfo.value.type,
      uValue: editingWindowInfo.value.uValue,
      shgc: editingWindowInfo.value.type === 'window' ? editingWindowInfo.value.shgc : 0
    };

    // 调用 renderFaceGroupInUpperViewport 重新渲染当前面组
    renderFaceGroupInUpperViewport(currentGroup);

    console.log('保存门窗尺寸成功');
  } else {
    console.error('未找到要更新的门窗');
  }
};

// 计算形状系数
const calculateShapeCoefficient = (perimeter: number, area: number): number => {
  if (area <= 0 || perimeter <= 0) return 0;
  return (perimeter * perimeter) / (4 * Math.PI * area);
};

// 添加设置窗口类型的函数
const setWindowType = (type: 'window' | 'door') => {
  if (editingWindowInfo.value) {
    editingWindowInfo.value.type = type;

    // 当类型改变时，调整SHGC值
    if (type === 'door') {
      editingWindowInfo.value.shgc = 0; // 门的SHGC固定为0
    } else if (type === 'window' && editingWindowInfo.value.shgc === 0) {
      editingWindowInfo.value.shgc = 0.5; // 如果之前是门（SHGC为0），切换为窗时设置默认值0.5
    }

    updateWindowDimensions(); // 更新门窗信息

    // 更新当前面组的子面类型系数
    if (currentSelectedGroupIndex.value !== null) {
      const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
      currentGroup.subFaceTypeCoefficient = calculateSubFaceTypeCoefficient(currentGroup.windows);

      // 更新子面总面积
      currentGroup.subFaceTotalArea = calculateSubFaceTotalArea(currentGroup.windows);

      // 更新子面U值
      currentGroup.subFaceUValue = calculateSubFaceUValue(currentGroup.windows);

      // 更新子面SHGC值
      currentGroup.subFaceSHGC = calculateSubFaceSHGC(currentGroup.windows);
    }
  }
};

// 计算子面类型系数
const calculateSubFaceTypeCoefficient = (windows: FaceGroup['windows']): number => {
  if (windows.length === 0) return 0; // 无门窗

  let hasWindow = false;
  let hasDoor = false;

  for (const item of windows) {
    if (item.type === 'window') hasWindow = true;
    if (item.type === 'door') hasDoor = true;

    // 如果已经找到了窗和门，就可以提前返回结果
    if (hasWindow && hasDoor) return 3;
  }

  if (hasWindow) return 1; // 只有窗
  if (hasDoor) return 2; // 只有门
  return 0; // 默认无门窗（理论上不会到这里）
};

// 计算子面总面积
const calculateSubFaceTotalArea = (windows: FaceGroup['windows']): number => {
  let totalArea = 0;
  for (const item of windows) {
    totalArea += item.width * item.height;
  }
  return totalArea;
};

// 创建计算子面U值的函数
const calculateSubFaceUValue = (windows: FaceGroup['windows']): number => {
  if (windows.length === 0) return 0; // 如果没有子面，返回0

  let totalArea = 0;
  let weightedUValue = 0;

  // 计算每个窗户的面积及其U值乘以面积
  for (const item of windows) {
    const area = item.width * item.height;
    totalArea += area;
    weightedUValue += area * item.uValue;
  }

  // 返回加权平均值
  return totalArea > 0 ? weightedUValue / totalArea : 0;
};

// 添加更新子面U值的函数 - 已废弃，U值现在完全由子面属性计算得出
const updateSubFaceUValue = (event: Event) => {
  if (!event.target || currentSelectedGroupIndex.value === null) return;

  const input = event.target as HTMLInputElement;
  let newValue = parseFloat(input.value);

  // 验证范围
  if (isNaN(newValue)) {
    newValue = 1.5; // 默认值
  } else if (newValue < 0.5) {
    newValue = 0.5; // 最小值
  } else if (newValue > 6) {
    newValue = 6; // 最大值
  }

  // 只有当面组有子面时才允许更新
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  if (currentGroup.windows && currentGroup.windows.length > 0) {
    currentGroup.subFaceUValue = newValue;

    // 强制更新面组数据以确保视图更新
    faceGroups.value = [...faceGroups.value];

    console.log(`更新了面组 ${currentSelectedGroupIndex.value + 1} 的子面U值为: ${newValue.toFixed(2)}`);
  } else {
    console.warn('当前面组没有子面，不能修改U值');
    // 重置回原来的值
    input.value = currentGroup.subFaceUValue.toString();
  }
};

// 添加计算子面SHGC的函数
const calculateSubFaceSHGC = (windows: FaceGroup['windows']): number => {
  if (windows.length === 0) return 0; // 如果没有子面，返回0

  let totalArea = 0;
  let weightedSHGC = 0;

  // 计算每个窗户的面积及其SHGC乘以面积
  for (const item of windows) {
    const area = item.width * item.height;
    totalArea += area;
    weightedSHGC += area * item.shgc;
  }

  // 返回加权平均值
  return totalArea > 0 ? weightedSHGC / totalArea : 0;
};

// 添加更新子面SHGC的函数 - 已废弃，SHGC值现在完全由子面属性计算得出
const updateSubFaceSHGC = (event: Event) => {
  if (!event.target || currentSelectedGroupIndex.value === null) return;

  const input = event.target as HTMLInputElement;
  let newValue = parseFloat(input.value);

  // 验证范围
  if (isNaN(newValue)) {
    newValue = 0.5; // 默认值
  } else if (newValue < 0) {
    newValue = 0; // 最小值
  } else if (newValue > 1) {
    newValue = 1; // 最大值
  }

  // 只有当面组有子面时才允许更新
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  if (currentGroup.windows && currentGroup.windows.length > 0) {
    currentGroup.subFaceSHGC = newValue;

    // 强制更新面组数据以确保视图更新
    faceGroups.value = [...faceGroups.value];

    console.log(`更新了面组 ${currentSelectedGroupIndex.value + 1} 的子面SHGC为: ${newValue.toFixed(2)}`);
  } else {
    console.warn('当前面组没有子面，不能修改SHGC');
    // 重置回原来的值
    input.value = currentGroup.subFaceSHGC.toString();
  }
};

// 添加更新导热系数的函数
const updateConductivity = (event: Event) => {
  if (!event.target || currentSelectedGroupIndex.value === null) return;

  const input = event.target as HTMLInputElement;
  let newValue = parseFloat(input.value);

  // 验证范围
  if (isNaN(newValue)) {
    newValue = 1; // 默认值
  } else if (newValue < 0.1) {
    newValue = 0.1; // 最小值
  } else if (newValue > 2) {
    newValue = 2; // 最大值
  }

  // 更新导热系数（不受子面限制，总是可以更新）
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  currentGroup.conductivity = newValue;

  // 强制更新面组数据以确保视图更新
  faceGroups.value = [...faceGroups.value];

  console.log(`更新了面组 ${currentSelectedGroupIndex.value + 1} 的导热系数为: ${newValue.toFixed(2)}`);
};

// 添加更新厚度的函数
const updateThickness = (event: Event) => {
  if (!event.target || currentSelectedGroupIndex.value === null) return;

  const input = event.target as HTMLInputElement;
  let newValue = parseFloat(input.value);

  // 验证范围
  if (isNaN(newValue)) {
    newValue = 0.2; // 默认值
  } else if (newValue < 0.1) {
    newValue = 0.1; // 最小值
  } else if (newValue > 0.5) {
    newValue = 0.5; // 最大值
  }

  // 更新厚度（不受子面限制，总是可以更新）
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  currentGroup.thickness = newValue;

  // 强制更新面组数据以确保视图更新
  faceGroups.value = [...faceGroups.value];

  console.log(`更新了面组 ${currentSelectedGroupIndex.value + 1} 的厚度为: ${newValue.toFixed(2)}`);
};

// 添加更新长波辐射吸收比的函数
const updateLongwaveAbsorptance = (event: Event) => {
  if (!event.target || currentSelectedGroupIndex.value === null) return;

  const input = event.target as HTMLInputElement;
  let newValue = parseFloat(input.value);

  // 验证范围
  if (isNaN(newValue)) {
    newValue = 0.9; // 默认值
  } else if (newValue < 0) {
    newValue = 0; // 最小值
  } else if (newValue > 1) {
    newValue = 1; // 最大值
  }

  // 更新长波辐射吸收比（不受子面限制，总是可以更新）
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  currentGroup.longwaveAbsorptance = newValue;

  // 强制更新面组数据以确保视图更新
  faceGroups.value = [...faceGroups.value];

  console.log(`更新了面组 ${currentSelectedGroupIndex.value + 1} 的长波辐射吸收比为: ${newValue.toFixed(2)}`);
};

// 添加更新太阳辐射吸收比的函数
const updateSolarAbsorptance = (event: Event) => {
  if (!event.target || currentSelectedGroupIndex.value === null) return;

  const input = event.target as HTMLInputElement;
  let newValue = parseFloat(input.value);

  // 验证范围
  if (isNaN(newValue)) {
    newValue = 0.7; // 默认值
  } else if (newValue < 0) {
    newValue = 0; // 最小值
  } else if (newValue > 1) {
    newValue = 1; // 最大值
  }

  // 更新太阳辐射吸收比（不受子面限制，总是可以更新）
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  currentGroup.solarAbsorptance = newValue;

  // 强制更新面组数据以确保视图更新
  faceGroups.value = [...faceGroups.value];

  console.log(`更新了面组 ${currentSelectedGroupIndex.value + 1} 的太阳辐射吸收比为: ${newValue.toFixed(2)}`);
};

// 添加更新可见光辐射吸收比的函数
const updateVisibleAbsorptance = (event: Event) => {
  if (!event.target || currentSelectedGroupIndex.value === null) return;

  const input = event.target as HTMLInputElement;
  let newValue = parseFloat(input.value);

  // 验证范围
  if (isNaN(newValue)) {
    newValue = 0.7; // 默认值
  } else if (newValue < 0) {
    newValue = 0; // 最小值
  } else if (newValue > 1) {
    newValue = 1; // 最大值
  }

  // 更新可见光辐射吸收比（不受子面限制，总是可以更新）
  const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
  currentGroup.visibleAbsorptance = newValue;

  // 强制更新面组数据以确保视图更新
  faceGroups.value = [...faceGroups.value];

  console.log(`更新了面组 ${currentSelectedGroupIndex.value + 1} 的可见光辐射吸收比为: ${newValue.toFixed(2)}`);
};

// 导出表格数据到Excel
const exportToExcel = async () => {
  try {
    // 如果邻接矩阵为空，先计算一次
    if (adjacencyMatrix.value.length === 0) {
      calculateAdjacencyMatrix();
    }

    // 导出邻接矩阵
    //exportAdjacencyMatrixToExcel();

    // 导出面组表格
    //exportFaceGroupsTable();

    console.log('表格导出成功!');

    // 发送JSON数据到本地服务器并等待响应
    const serverResponse = await sendJsonToLocalServer();

    // 导航到第三个界面，并将响应数据作为参数传递
    if (serverResponse.success) {
      router.push({
        path: '/third',
        query: { response: JSON.stringify(serverResponse.data || { message: serverResponse.message }) }
      });
    } else {
      router.push({
        path: '/third',
        query: { response: JSON.stringify({ error: serverResponse.message }) }
      });
    }
  } catch (error: any) {
    console.error('导出表格失败:', error);
    // 出错时也导航到第三个界面，但带有错误信息
    router.push({
      path: '/third',
      query: { response: JSON.stringify({ error: error.message }) }
    });
  }
};

// 导出邻接矩阵为Excel
const exportAdjacencyMatrixToExcel = () => {
  // 如果邻接矩阵为空，先计算
  if (adjacencyMatrix.value.length === 0) {
    calculateAdjacencyMatrix();
  }

  // 创建匹配邻接矩阵大小的数据数组
  const matrix = adjacencyMatrix.value;
  const size = matrix.length;

  // 创建数据行
  const rows: string[][] = [];

  for (let i = 0; i < size; i++) {
    const dataRow: string[] = [];
    for (let j = 0; j < size; j++) {
      dataRow.push(matrix[i][j].toString());
    }
    rows.push(dataRow);
  }

  // 创建工作簿
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(rows);

  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(wb, ws, '邻接矩阵');

  // 生成Excel文件并触发下载
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  saveAs(blob, 'adjmatrix.xlsx');

  console.log('邻接矩阵已导出');
};

// 导出邻接矩阵为CSV
const exportAdjacencyMatrixToCSV = () => {
  // 如果邻接矩阵为空，先计算
  if (adjacencyMatrix.value.length === 0) {
    calculateAdjacencyMatrix();
  }

  const matrix = adjacencyMatrix.value;
  const size = matrix.length;

  // 创建CSV内容
  let csvContent = '';

  // 添加数据行
  for (let i = 0; i < size; i++) {
    const row = matrix[i].join(',');
    csvContent += row + '\n';
  }

  // 创建Blob并下载
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, 'adjacency_matrix.csv');

  console.log('邻接矩阵CSV已导出');
};

// 导出原始节点数据为CSV
const exportNodeDataToCSV = () => {
  const nodeData: any[] = [];

  // 添加表头（严格按照API格式）
  const headers = ['Name', 'Type', 'RClass', 'Out', 'Area', 'SI', 'SType', 'SArea', 'SCon', 'SSHGC', 'Con', 'Thi', 'TA', 'SA', 'VA', 'Dir'];

  nodeData.push(headers);

  // 添加面组数据
  faceGroups.value.forEach((group, index) => {
    // 处理方向值转换
    let directionValue = 0; // 默认值
    switch (group.direction) {
      case "东":
        directionValue = 1;
        break;
      case "南":
        directionValue = 2;
        break;
      case "西":
        directionValue = 3;
        break;
      case "北":
        directionValue = 4;
        break;
      case "上":
      case "下":
        directionValue = 0;
        break;
    }

    // 创建节点数据行（type字段全部填0）
    const nodeRow = [
      0,  // type字段全部填0
      group.category,
      group.regionClass || 0,
      group.externalCondition,
      group.area.toFixed(2),
      group.shapeCoefficient.toFixed(2),
      group.subFaceTypeCoefficient,
      group.subFaceTotalArea.toFixed(2),
      group.subFaceUValue.toFixed(2),
      group.subFaceSHGC.toFixed(2),
      group.conductivity.toFixed(2),
      group.thickness.toFixed(2),
      group.longwaveAbsorptance.toFixed(2),
      group.solarAbsorptance.toFixed(2),
      group.visibleAbsorptance.toFixed(2),
      directionValue
    ];

    nodeData.push(nodeRow);
  });

  // 创建CSV内容
  let csvContent = '';
  nodeData.forEach(row => {
    csvContent += row.join(',') + '\n';
  });

  // 创建Blob并下载
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, 'node_data.csv');

  console.log('原始节点数据CSV已导出');
};

// 导出节点重要性为CSV
const exportNodeImportanceToCSV = () => {
  if (!apiResponse.value?.explanation?.node_importance) {
    alert(currentLanguage.value === 'zh' ? '没有节点重要性数据可导出' : 'No node importance data to export');
    return;
  }

  const nodeImportance = apiResponse.value.explanation.node_importance;

  // 获取特征列表（排除Node_ID）
  const allFeatures = Object.keys(nodeImportance).filter(key => key !== 'Node_ID');

  if (allFeatures.length === 0) {
    alert(currentLanguage.value === 'zh' ? '没有可用的特征数据' : 'No feature data available');
    return;
  }

  // 定义固定的特征顺序（与界面3一致）
  const featureOrder = [
    'Area', 'SI', 'NoDirection', 'East', 'South', 'West', 'North',
    'exterior', 'interior', 'ground', 'roof', 'Res', 'Thickness',
    'ThermalAbsorptance', 'SolarAbsorptance', 'VisiblAbsorptance',
    'Outdoors', 'Surface', 'Ground', 'NoSubface', 'Window', 'Door',
    'Window&Door', 'SubfaceArea', 'SubRes', 'SubSHGC'
  ];

  // 过滤出存在的特征并按顺序排列
  const orderedFeatures = featureOrder
    .filter(feature => allFeatures.includes(feature))
    .concat(allFeatures.filter(feature => !featureOrder.includes(feature)));

  // 获取节点数量（从第一个特征的数据中获取）
  const firstFeature = orderedFeatures[0];
  const featureData = nodeImportance[firstFeature];
  const nodeCount = featureData ? Object.keys(featureData).length : 0;

  if (nodeCount === 0) {
    alert(currentLanguage.value === 'zh' ? '没有可用的节点数据' : 'No node data available');
    return;
  }

  // 创建CSV内容
  let csvContent = '';

  // 添加表头：Node, 然后是各个特征名
  csvContent += 'Node,' + orderedFeatures.join(',') + '\n';

  // 添加每个节点的数据行
  for (let index = 0; index < nodeCount; index++) {
    const row = [`Node ${index}`];
    orderedFeatures.forEach(feature => {
      const value = nodeImportance[feature]?.[index];
      row.push(value !== undefined ? parseFloat(String(value)).toFixed(2) : '0.00');
    });
    csvContent += row.join(',') + '\n';
  }

  // 创建Blob并下载
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, 'node_importance.csv');

  console.log('节点重要性CSV已导出');
};

// 导出边重要性为CSV
const exportEdgeImportanceToCSV = () => {
  if (!apiResponse.value?.explanation?.edge_matrix) {
    alert(currentLanguage.value === 'zh' ? '没有链接重要性数据可导出' : 'No edge importance data to export');
    return;
  }

  const edgeMatrix = apiResponse.value.explanation.edge_matrix;
  const size = edgeMatrix.length;

  // 创建CSV内容
  let csvContent = '';

  // 添加表头：第一列是空的，后面是节点编号
  csvContent += ',';
  for (let i = 0; i < size; i++) {
    csvContent += `Node ${i}`;
    if (i < size - 1) csvContent += ',';
  }
  csvContent += '\n';

  // 添加数据行
  for (let i = 0; i < size; i++) {
    csvContent += `Node ${i},`;
    for (let j = 0; j < size; j++) {
      csvContent += parseFloat(String(edgeMatrix[i][j])).toFixed(2);
      if (j < size - 1) csvContent += ',';
    }
    csvContent += '\n';
  }

  // 创建Blob并下载
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  saveAs(blob, 'edge_importance.csv');

  console.log('链接重要性CSV已导出');
};

// 将数据发送到本地服务器
const sendJsonToLocalServer = (): Promise<{success: boolean, message: string, data?: any}> => {
  return new Promise((resolve) => {
    try {
      // 如果邻接矩阵为空，先计算
      if (adjacencyMatrix.value.length === 0) {
        calculateAdjacencyMatrix();
      }

      // 准备节点数据数组
      const nodeData: any[] = [];

      // 添加面组数据
      faceGroups.value.forEach((group, index) => {
        // 处理方向属性转换
        let directionValue = 0; // 默认值
        switch (group.direction) {
          case "东":
            directionValue = 1;
            break;
          case "南":
            directionValue = 2;
            break;
          case "西":
            directionValue = 3;
            break;
          case "北":
            directionValue = 4;
            break;
          case "上":
          case "下":
            directionValue = 0;
            break;
        }

        // 创建节点数据行，格式与示例保持一致
        const nodeRow = [
          group.type,
          group.category,
          group.regionClass || 0,
          group.externalCondition,
          parseFloat(group.area.toFixed(2)),
          parseFloat(group.shapeCoefficient.toFixed(2)),
          group.subFaceTypeCoefficient,
          parseFloat(group.subFaceTotalArea.toFixed(2)),
          parseFloat(group.subFaceUValue.toFixed(2)),
          parseFloat(group.subFaceSHGC.toFixed(2)),
          parseFloat(group.conductivity.toFixed(2)),
          parseFloat(group.thickness.toFixed(2)),
          parseFloat(group.longwaveAbsorptance.toFixed(2)),
          parseFloat(group.solarAbsorptance.toFixed(2)),
          parseFloat(group.visibleAbsorptance.toFixed(2)),
          directionValue
        ];

        nodeData.push(nodeRow);
      });

      // 准备邻接矩阵数据
      const matrix = adjacencyMatrix.value;
      const adjMatrix: number[][] = [];

      for (let i = 0; i < matrix.length; i++) {
        const row: number[] = [];
        for (let j = 0; j < matrix[i].length; j++) {
          row.push(matrix[i][j]);
        }
        adjMatrix.push(row);
      }

      // 创建最终的JSON数据对象
      const jsonData = {
        node_data: nodeData,
        adj_matrix: adjMatrix,
        wall_type: optimizationParams.value.wallMaterial,
        population_size: optimizationParams.value.populationSize,
        generations: optimizationParams.value.iterations,
        stream: false
      };

      // 发送POST请求到本地端口5000
      const API_URL_OPT = import.meta.env.VITE_API_URL_OPT || import.meta.env.VITE_API_URL || 'http://localhost:5001';
      fetch(`${API_URL_OPT}/optimize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData)
      })
      .then(async response => {
        // 尝试解析响应，即使状态码不是200
        let data;
        try {
          data = await response.json();
        } catch (e) {
          // 如果无法解析JSON，返回文本错误
          const text = await response.text();
          throw new Error(`服务器错误 (${response.status}): ${text || response.statusText}`);
        }
        
        // 如果HTTP状态码不是200-299，或者后端返回success=false，抛出错误
        if (!response.ok) {
          const errorMsg = data.error || data.message || `HTTP错误: ${response.status}`;
          throw new Error(errorMsg);
        }
        
        return data;
      })
      .then(data => {
        console.log('JSON数据成功发送到本地服务器:', data);
        // 检查后端返回的success字段
        if (data.success === false) {
          // 如果后端返回错误，传递错误信息
          resolve({
            success: false,
            message: data.error || "优化失败",
            data: data
          });
        } else {
          // 保存完整的响应数据
          resolve({
            success: true,
            message: data.message || "数据接收成功",
            data: data
          });
        }
      })
      .catch(error => {
        console.error('发送JSON数据到本地服务器失败:', error);
        const API_URL_OPT = import.meta.env.VITE_API_URL_OPT || import.meta.env.VITE_API_URL || 'http://localhost:5001';
        
        let errorMessage = error.message || '未知错误';
        
        // 针对 "Failed to fetch" 错误提供更详细的说明
        if (error.message && (error.message.includes('Failed to fetch') || error.message.includes('NetworkError'))) {
          errorMessage = `无法连接到优化服务 (${API_URL_OPT})\n\n可能的原因：\n1. 优化API服务未启动\n2. 服务运行在不同的端口\n3. 网络连接问题\n\n解决方法：\n1. 进入后端目录: cd gcn_backend-gpu--main\n2. 运行优化服务: python optimization_api.py\n3. 或者运行: python start_apis.py (同时启动两个服务)\n4. 确保服务运行在端口 5001`;
        }
        
        resolve({ success: false, message: errorMessage });
      });

    } catch (error: any) {
      console.error('准备JSON数据失败:', error);
      resolve({ success: false, message: `准备数据失败: ${error.message}` });
    }
  });
};


// 导出面组表格
const exportFaceGroupsTable = () => {
  // 准备表头（但不添加到导出数据中）
  const headers = [
    '类型', '大类', '区域类', '外接条件',
    '面积', '形状系数', '子面类型系数', '子面总面积',
    '子面U值', '子面SHGC', '导热系数', '厚度',
    '长波辐射吸收比', '太阳辐射吸收比', '可见光辐射吸收比', '朝向'
  ];

  // 准备表格数据
  const tableData: string[][] = [];
  // 不添加表头: tableData.push(headers);

  // 添加行数据
  faceGroups.value.forEach((group, index) => {
    // 处理方向属性转换
    let directionValue = "0"; // 默认值
    switch (group.direction) {
      case "东":
        directionValue = "1";
        break;
      case "南":
        directionValue = "2";
        break;
      case "西":
        directionValue = "3";
        break;
      case "北":
        directionValue = "4";
        break;
      case "上":
      case "下":
        directionValue = "0";
        break;
    }

    const rowData = [
      group.type,
      group.category,
      (group.regionClass || 0).toString(),
      group.externalCondition,
      group.area.toFixed(2),
      group.shapeCoefficient.toFixed(2),
      group.subFaceTypeCoefficient.toString(),
      group.subFaceTotalArea.toFixed(2),
      group.subFaceUValue.toFixed(2),
      group.subFaceSHGC.toFixed(2),
      group.conductivity.toFixed(2),
      group.thickness.toFixed(2),
      group.longwaveAbsorptance.toFixed(2),
      group.solarAbsorptance.toFixed(2),
      group.visibleAbsorptance.toFixed(2),
      directionValue
    ];
    tableData.push(rowData);
  });

  // 创建工作簿
  const wb = XLSX.utils.book_new();
  const ws = XLSX.utils.aoa_to_sheet(tableData);

  // 添加工作表到工作簿
  XLSX.utils.book_append_sheet(wb, ws, '面组数据');

  // 生成Excel文件并触发下载
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
  saveAs(blob, 'node.xlsx');

  console.log('面组表格已导出');
};

// 添加 orderedFeatures 计算属性
const orderedFeatures = computed(() => {
  if (!apiResponse.value?.explanation?.node_importance) return [];

  // 定义固定的特征顺序
  const featureOrder = [
    'Area', 'SI', 'NoDirection', 'East', 'South', 'West', 'North',
    'exterior', 'interior', 'ground', 'roof', 'Res', 'Thickness',
    'ThermalAbsorptance', 'SolarAbsorptance', 'VisiblAbsorptance',
    'Outdoors', 'Surface', 'Ground', 'NoSubface', 'Window', 'Door',
    'Window&Door', 'SubfaceArea', 'SubRes', 'SubSHGC'
  ];

  // 过滤出存在于API响应中的特征，并按定义的顺序排序
  const availableFeatures = Object.keys(apiResponse.value.explanation.node_importance)
    .filter(key => key !== 'Node_ID');

  return featureOrder
    .filter(feature => availableFeatures.includes(feature))
    .concat(availableFeatures.filter(feature => !featureOrder.includes(feature)));
});

// 添加特征名称映射函数
const getDisplayName = (feature: string): string => {
  const nameMap: Record<string, string> = {
    'Area': 'Area',
    'SI': 'SI',
    'NoDirection': 'Dir0',
    'East': 'Dir1',
    'South': 'Dir2',
    'West': 'Dir3',
    'North': 'Dir4',
    'exterior': 'Type0',
    'interior': 'Type1',
    'ground': 'Type2',
    'roof': 'Type3',
    'Res': 'Con',
    'Thickness': 'Thi',
    'ThermalAbsorptance': 'TA',
    'SolarAbsorptance': 'SA',
    'VisiblAbsorptance': 'VA',
    'Outdoors': 'Out0',
    'Surface': 'Out1',
    'Ground': 'Out2',
    'NoSubface': 'SType0',
    'Window': 'SType1',
    'Door': 'SType2',
    'Window&Door': 'SType3',
    'SubfaceArea': 'SArea',
    'SubRes': 'SCon',
    'SubSHGC': 'SSHGC'
  };

  return nameMap[feature] || feature;
};

// 坐标缩放函数
const getScaledX = (cost: number): number => {
  if (paretoSolutions.value.length === 0) return 200;

  const costs = paretoSolutions.value.map(s => s.cost);
  const minCost = Math.min(...costs);
  const maxCost = Math.max(...costs);

  if (maxCost === minCost) return 200; // 如果所有值相同，放在中间

  // 将价格映射到SVG坐标 (70-330)，留出边距避免画在坐标轴端点
  return 70 + ((cost - minCost) / (maxCost - minCost)) * 260;
};

const getScaledY = (energy: number): number => {
  if (paretoSolutions.value.length === 0) return 150;

  const energies = paretoSolutions.value.map(s => s.energy);
  const minEnergy = Math.min(...energies);
  const maxEnergy = Math.max(...energies);

  if (maxEnergy === minEnergy) return 150; // 如果所有值相同，放在中间

  // 将能耗映射到SVG坐标 (230-70)，留出边距避免画在坐标轴端点
  return 230 - ((energy - minEnergy) / (maxEnergy - minEnergy)) * 160;
};
</script>

<style>
/* 全局样式，防止滚动条出现 */
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  width: 100%;
  height: 100%;
}
</style>

<style scoped>
.author-info {
  font-size: 8px;
  text-align: center;
  position: absolute;
  bottom: -15px;
  width: 100%;
  height: 50px;
  background-color: #f0f0f000;
  z-index: 9999;
}
.home {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f0f0;
  box-sizing: border-box;
  position: fixed;
  top: 0;
  left: 0;
  overflow: hidden;
  padding: 0 2.5%;
}

.viewport-container {
  width: 47.5%;
  height: 92%;
  bottom: 10px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
  margin-right: 2.5%;
}

.right-container {
  width: 47.5%;
  height: 92%;
  bottom: 10px;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 2px;
  justify-content: space-between;
}

.right-panel {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  position: relative;
}

.upper-panel {
  height: calc((100% - 2px) );
}

.lower-panel {
  height: calc((95% - 2px) * 1/3);
}

.panel-header {
  background-color: #333;
  color: white;
  padding: 15px;
  text-align: center;
}

.panel-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: normal;
}

.panel-content {
  padding: 20px;
  flex: 1;
  overflow-y: auto;
  margin-top: 10px; /* 添加上边距，为刘海屏腾出空间 */
}

.canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
  position: absolute;
  top: 0;
  left: 0;
}

.controls {
  position: absolute;
  top: 15px;
  left: 15px;
  z-index: 10;
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 300px;
}

.back-button {
  padding: 8px 12px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s;
  display: flex;
  align-items: center;
}

.back-button:hover {
  background-color: #d32f2f;
}

.back-icon {
  margin-right: 5px;
  font-size: 14px;
}

/* 刘海屏标签样式 */
.notch-container {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  gap: 10px;
}

.upper-notch {
  top: 0;
  left: 50%;
}

.notch {
  background-color: #333;
  color: white;
  padding: 4px 12px 6px 12px;
  border-bottom-left-radius: 8px;
  border-bottom-right-radius: 8px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: background-color 0.3s ease;
  min-width: 60px;
  max-width: 200px;
  width: auto;
  display: inline-block;
}

.notch.selected {
  background-color: #4CAF50;
}

.notch:hover {
  background-color: #555;
}

.notch.selected:hover {
  background-color: #45a049;
}

.notch::before {
  content: "";
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 4px;
  background-color: #333;
  border-bottom-left-radius: 10px;
  border-bottom-right-radius: 10px;
  transition: background-color 0.3s ease;
}

.notch.selected::before {
  background-color: #4CAF50;
}

.notch-text {
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 0.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: 100%;
}

/* 空表格样式 */
.empty-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.empty-table th, .empty-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.empty-table th {
  background-color: #f2f2f2;
  font-weight: bold;
  font-size: 12px;
}

.empty-table tbody tr:hover {
  background-color: #f5f5f5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .home {
    flex-direction: column;
    justify-content: flex-start;
    padding: 10px 2.5%;
  }

  .viewport-container {
    width: 100%;
    height: 45%;
    border-radius: 16px;
    margin-bottom: 10px;
    margin-right: 0;
  }

  .right-container {
    width: 100%;
    height: 45%;
    gap: 2px;
  }

  .upper-panel {
    height: calc((45% - 2px) * 2/3);
  }

  .lower-panel {
    height: calc((45% - 2px) * 1/3);
  }

  .notch {
    padding: 3px 8px 4px 8px;
  }

  .notch-text {
    font-size: 6px;
  }

  .back-button {
    padding: 6px 10px;
    font-size: 10px;
  }

  .back-icon {
    font-size: 12px;
  }

  .panel-header h2 {
    font-size: 14px;
  }

  .panel-content {
    padding: 10px;
  }

  .empty-table th {
    font-size: 10px;
    padding: 4px;
  }
}

/* 面信息样式 */
.face-info {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.face-info h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.info-row {
  display: flex;
  margin-bottom: 8px;
}

.info-label {
  font-weight: bold;
  width: 80px;
  color: #555;
}

.info-value {
  flex: 1;
}

.no-selection {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-style: italic;
}

.no-data {
  text-align: center;
  color: #999;
  font-style: italic;
  padding: 10px;
}

.action-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
}

.action-button:hover {
  background-color: #45a049;
}

.mode-button {
  padding: 6px 10px;
  background-color: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  flex: 1;
  transition: background-color 0.3s;
}

.mode-button:hover {
  background-color: #d0d0d0;
}

.mode-button.active {
  background-color: #4CAF50;
  color: white;
}

.full-width-button {
  padding: 6px 10px;
  background-color: #e0e0e0;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  width: 100%;
  margin-top: 5px;
  transition: background-color 0.3s;
}

.full-width-button:hover {
  background-color: #d0d0d0;
}

/* 父面信息样式 */
.parent-faces-section {
  margin-top: 15px;
  border-top: 1px dashed #ddd;
  padding-top: 10px;
}

.parent-faces-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  color: #555;
}

.parent-face-item {
  background-color: #f0f8ff;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 8px;
  border-left: 3px solid #4CAF50;
}

.parent-face-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.parent-label {
  font-weight: bold;
  color: #333;
}

.parent-value {
  color: #666;
}

/* 子交集面样式 */
.child-intersections-section {
  margin-top: 15px;
  border-top: 1px dashed #ddd;
  padding-top: 10px;
}

.child-intersections-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  color: #555;
}

.child-intersection-item {
  background-color: #f0f8ff;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 8px;
  border-left: 3px solid #4CAF50;
}

.child-intersection-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.child-label {
  font-weight: bold;
  color: #333;
}

.child-value {
  color: #666;
}

/* 显示裁剪面所属的原始面信息 */
.parent-face-section {
  margin-top: 15px;
  border-top: 1px dashed #ddd;
  padding-top: 10px;
}

.parent-face-item {
  background-color: #f0f8ff;
  border-radius: 4px;
  padding: 8px;
  margin-bottom: 8px;
  border-left: 3px solid #4CAF50;
}

.parent-face-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.parent-label {
  font-weight: bold;
  color: #333;
}

.parent-value {
  color: #666;
}

/* 添加交集面和裁剪面组表格样式 */
.face-groups-section {
  margin-top: 15px;
  border-top: 1px dashed #ddd;
  padding-top: 10px;
}

.face-groups-section h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  color: #333;
}

.table-container {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
}

.face-groups-table {
  width: 100%;
  border-collapse: collapse;
}

.face-groups-table th, .face-groups-table td {
  border: 1px solid #ddd;
  padding: 6px;
  text-align: left;
  font-size: 6px;
}

.face-groups-table th {
  background-color: #f2f2f2;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
}

.face-groups-table tbody tr:hover {
  background-color: #f5f5f5;
}

.intersection-row {
  background-color: #fff8e1; /* 浅黄色背景 */
}

.clipped-row {
  background-color: #e1f5fe; /* 浅蓝色背景 */
}

.intersection-row:hover {
  background-color: #ffecb3; /* 深一点的黄色 */
}

.clipped-row:hover {
  background-color: #b3e5fc; /* 深一点的蓝色 */
}

/* 邻接矩阵弹窗样式 */
.matrix-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.matrix-dialog {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.matrix-dialog-header {
  padding: 12px 15px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.matrix-dialog-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 0;
  margin: 0;
  line-height: 1;
}

.matrix-dialog-content {
  padding: 15px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  max-height: calc(90vh - 50px);
}

.matrix-description {
  margin-bottom: 10px;
}

.matrix-description p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.matrix-table-container {
  overflow: auto;
  flex: 1;
  border: 1px solid #eee;
  border-radius: 4px;
}

.adjacency-matrix {
  border-collapse: collapse;
  width: 100%;
  table-layout: fixed;
}

.adjacency-matrix th, .adjacency-matrix td {
  border: 1px solid #ddd;
  padding: 4px 2px;
  text-align: center;
  font-size: 7px; /* 将字体大小从14px减小到7px */
  min-width: 30px; /* 减小最小宽度以适应更小的字体 */
  height: 30px; /* 减小高度以适应更小的字体 */
}

.adjacency-matrix .index-cell {
  background-color: #f2f2f2;
  font-weight: bold;
  position: sticky;
  z-index: 2;
  min-width: 30px; /* 减小最小宽度以适应更小的字体 */
  width: 30px; /* 减小宽度以适应更小的字体 */
}

.adjacency-matrix thead th {
  position: sticky;
  top: 0;
  z-index: 3;
  background-color: #f2f2f2;
}

.adjacency-matrix tbody th {
  position: sticky;
  left: 0;
  z-index: 1;
}

.adjacency-matrix thead th:first-child {
  position: sticky;
  top: 0;
  left: 0;
  z-index: 4;
}

.connected {
  background-color: #d3d3d3;
}

.self {
  background-color: #e0e0e0;
}

.no-content {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-size: 16px;
  font-style: italic;
}

.upper-canvas {
  width: 100% !important;
  height: 100% !important;
  display: block;
}

/* 添加侧边栏样式 */
.panel-content {
  position: relative;
  width: 100%;
  height: 100%;
}

.upper-canvas {
  width: 100%;
  height: 100%;
}

.upper-sidebar {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 10;
  font-size: 14px;
  transition: width 0.3s ease;
  width: 180px;
  display: flex;
}

.upper-sidebar.collapsed {
  width: 24px;
  padding: 0;
}

.sidebar-toggle {
  width: 24px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  border-right: 1px solid #ddd;
}

.toggle-arrow {
  font-size: 20px;
  line-height: 1;
  transition: transform 0.3s ease;
  color: #666;
}

.toggle-arrow:hover {
  color: #333;
}

.toggle-arrow.collapsed {
  transform: rotate(180deg);
}

.sidebar-content {
  flex: 1;
  padding: 12px;
}

.upper-sidebar h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
  text-align: center;
  border-bottom: 1px solid #ddd;
  padding-bottom: 6px;
}

.property-item {
  margin-bottom: 6px;
  display: flex;
  justify-content: space-between;
}

.property-label {
  font-weight: bold;
  color: #555;
}

.property-value {
  color: #333;
}

/* 添加绘制门窗按钮样式 */
.draw-button {
  position: absolute;
  top: 10px;
  left: 10px;
  padding: 8px 16px;
  background-color: #ffffff;
  color: #333;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.draw-button:hover {
  background-color: #f5f5f5;
}

.draw-button.active {
  background-color: #ff4444;
  color: white;
  border-color: #ff4444;
}

/* 门窗信息提示样式 */
.window-info-tooltip {
  position: fixed;
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  border-radius: 4px;
  padding: 8px;
  font-size: 12px;
  pointer-events: auto; /* 修改为auto允许点击事件 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  min-width: 120px;
}

.window-info-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.window-info-item {
  display: flex;
  justify-content: space-between;
}

.window-info-label {
  font-weight: bold;
  margin-right: 8px;
}

.window-info-value {
  color: #4286f4;
}

/* 添加删除按钮样式 */
.window-info-action {
  margin-top: 8px;
  display: flex;
  justify-content: center;
}

.window-delete-button {
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 11px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.window-delete-button:hover {
  background-color: #d32f2f;
}

/* 添加保存按钮样式 */
.window-save-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 3px 8px;
  font-size: 11px;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-left: 5px;
}

.window-save-button:hover {
  background-color: #45a049;
}

/* 输入框样式 */
.window-info-input {
  width: 100%;
  padding: 5px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* 添加类型切换按钮样式 */
.window-type-toggle {
  display: flex;
  margin-left: 10px;
}

.type-toggle-btn {
  padding: 3px 10px;
  background: #e0e0e0;
  border: 1px solid #ccc;
  cursor: pointer;
  transition: all 0.2s;
}

.type-toggle-btn:first-child {
  border-radius: 4px 0 0 4px;
}

.type-toggle-btn:last-child {
  border-radius: 0 4px 4px 0;
}

.type-toggle-btn.active {
  background: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

/* 添加样式 */
.property-input {
  width: 60px;
  text-align: right;
  border: 1px solid #ccc;
  border-radius: 3px;
  padding: 2px 5px;
}

/* 导出按钮样式 */
.export-button-container {
  position: absolute;
  bottom: 15px;
  left: 15px;
  z-index: 10;
}

.export-button {
  padding: 8px 12px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s;
}

.export-button:hover {
  background-color: #0b7dda;
}

/* 添加侧边栏样式 */
.left-sidebar {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(255, 255, 255, 0.85);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  z-index: 10;
  font-size: 14px;
  transition: width 0.3s ease;
  width: 280px;
  display: flex;
  max-height: calc(100% - 20px);
  overflow: hidden;
}

.left-sidebar.collapsed {
  width: 24px;
  padding: 0;
}

.sidebar-toggle {
  width: 24px;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  border-right: 1px solid #ddd;
}

.toggle-arrow {
  font-size: 20px;
  line-height: 1;
  transition: transform 0.3s ease;
  color: #666;
}

.toggle-arrow:hover {
  color: #333;
}

.toggle-arrow.collapsed {
  transform: rotate(180deg);
}

.sidebar-content {
  flex: 1;
  padding: 12px;
  overflow-y: auto;
  max-height: 100%;
}

.left-sidebar h3 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 16px;
  color: #333;
  text-align: center;
  border-bottom: 1px solid #ddd;
  padding-bottom: 6px;
}

.property-item {
  margin-bottom: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
}

.property-label {
  font-weight: bold;
  color: #555;
  margin-right: 5px;
  min-width: 120px;
}

.property-value {
  color: #333;
  flex: 1;
  word-break: break-word;
}

.property-input {
  width: 80px;
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* 移除旧的右侧边栏样式 */
.upper-sidebar {
  display: none;
}

/* 添加API返回结果样式 */
.api-response {
  height: 100%;
  overflow: auto;
  padding: 10px;
}

.main-content-container {
  display: flex;
  width: 100%;
  height: 50%;
  gap: 20px;
  overflow: hidden;
  align-items: stretch;
}

.left-container {
  width: 33.33%;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
  padding-bottom: 15px;
}

.coordinate-container {
  width: 66.67%;
  flex-shrink: 0;
  background-color: #fafafa;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.coordinate-system {
  width: 100%;
  height: 100%;
  background-color: #fafafa;
}

.result-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.prediction-section {
  height: calc(30% - 5px);
  flex-shrink: 0;
  text-align: center;
  background-color: #f5f9ff;
}

.optimization-params-section {
  height: calc(70% - 10px);
  flex-shrink: 0;
  overflow-y: auto;
}

.result-section h3 {
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  font-size: 16px;
  color: #333;
}


.prediction-value {
  font-size: 18px;
  font-weight: bold;
  color: #2196F3;
  margin: 0px 0;
}

.optimization-params-section {
  background-color: #f9f9f9;
}

.param-item {
  margin-bottom: 6px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.param-item label {
  font-weight: bold;
  color: #555;
  font-size: 10px;
  white-space: nowrap;
  flex-shrink: 0;
}

.param-item input,
.param-item select {
  padding: 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 10px;
  background-color: white;
  max-width: 120px;
  flex-shrink: 0;
}

.param-item input:focus,
.param-item select:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 5px rgba(33, 150, 243, 0.3);
}

.select-wrapper {
  position: relative;
  max-width: 120px;
}

.select-display {
  padding: 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 10px;
  background-color: white;
  cursor: pointer;
  pointer-events: none;
}

.hidden-select {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.optimization-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 12px;
  cursor: pointer;
  display: block;
  margin: 0 auto;
}

.optimization-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 12px;
  height: 12px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.solution-details-container {
  width: 100%;
  min-height: 200px;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin-top: 20px;
}

.comparison-container {
  width: 100%;
  min-height: 200px;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin-top: 20px;
  display: flex;
  gap: 15px;
}

.export-container {
  width: 100%;
  min-height: 200px;
  background-color: #fff;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 四个基础导出按钮容器 */
.basic-export-buttons {
  width: 100%;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: stretch;
  gap: 10px;
}

/* 基础导出按钮样式 */
.basic-export-btn {
  flex: 1;
  min-width: 0;
  white-space: normal;
  word-wrap: break-word;
  word-break: break-word;
  padding: 12px 15px;
  line-height: 1.3;
  display: flex;
  align-items: center;
  justify-content: center;
}

.export-button {
  padding: 12px 30px;
  font-size: 10px;
  font-weight: bold;
  color: white;
  background-color: #4CAF50;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  transition: all 0.3s ease;
}

.export-button:hover {
  background-color: #45a049;
  box-shadow: 0 4px 8px rgba(0,0,0,0.3);
  transform: translateY(-2px);
}

.export-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.export-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.6;
}

.export-button:disabled:hover {
  background-color: #cccccc;
  transform: none;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

/* 导出优化方案区域 */
.solution-export-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.solution-select-label {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.solution-selector {
  width: 100%;
}

.solution-select {
  width: 100%;
  max-width: 300px;
  padding: 10px 15px;
  font-size: 14px;
  border: 2px solid #ddd;
  border-radius: 6px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.solution-select:hover {
  border-color: #4CAF50;
}

.solution-select:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.solution-select option:disabled {
  color: #ccc;
}

/* 已选方案标签容器 */
.selected-solutions-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  min-height: 40px;
  padding: 10px;
  background-color: white;
  border-radius: 6px;
  border: 2px dashed #ddd;
}

.selected-solutions-tags:empty::before {
  content: attr(data-placeholder);
  color: #999;
  font-style: italic;
}

/* 方案标签样式 */
.solution-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  animation: tagFadeIn 0.3s ease;
}

@keyframes tagFadeIn {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.solution-tag:hover {
  box-shadow: 0 3px 6px rgba(0,0,0,0.15);
  transform: translateY(-1px);
}

.tag-text {
  user-select: none;
}

.tag-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.2s ease;
  line-height: 1;
}

.tag-remove:hover {
  background-color: rgba(255, 255, 255, 0.5);
  transform: scale(1.1);
}

.export-solutions-btn {
  align-self: flex-start;
}

.comparison-left {
  width: 50%;
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 10px;
}

.comparison-right {
  width: 50%;
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 10px;
}

.comparison-controls {
  display: flex;
  flex-direction: row;
  gap: 15px;
  align-items: center;
}

.control-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.control-item label {
  font-weight: bold;
  color: #555;
  font-size: 10px;
  min-width: 40px;
}

.comparison-select {
  padding: 2px 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 10px;
  background-color: white;
  min-width: 80px;
}

.solution-summary {
  margin-top: 10px;
  padding: 8px;
  background-color: #f0f8ff;
  border-radius: 4px;
  display: flex;
  flex-direction: row;
  gap: 20px;
  justify-content: center;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.summary-label {
  font-size: 11px;
  font-weight: bold;
  color: #555;
}

.summary-value {
  font-size: 12px;
  font-weight: bold;
  color: #2196F3;
}

.material-info {
  margin-top: 15px;
}

.material-row {
  font-size: 10px;
  line-height: 1.2;
  margin-bottom: 3px;
  color: #333;
}

.comparison-chart {
  margin-top: 15px;
  display: flex;
  flex-direction: row;
  gap: 2px;
  justify-content: space-between;
}

.chart-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
}

.chart-label {
  font-size: 8px;
  font-weight: bold;
  color: #555;
  margin-top: 4px;
  text-align: center;
}

.chart-bars {
  display: flex;
  flex-direction: row;
  gap: 1px;
  align-items: flex-end;
  height: 85px;
}

.bar-before,
.bar-after {
  width: 24px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 1px;
  font-size: 8px;
  color: white;
  border-radius: 2px;
  min-height: 10px;
  position: relative;
}

.bar-before {
  background-color: #87CEEB;
}

.bar-after {
  background-color: #87CEEB; /* 默认淡蓝色，会被JavaScript动态覆盖 */
}

.solution-details-container h3 {
  margin-top: 0;
  margin-bottom: 15px;
  font-size: 16px;
  color: #333;
  text-align: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.materials-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.materials-table th,
.materials-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.materials-table th {
  background-color: #f2f2f2;
  font-weight: bold;
  position: sticky;
  top: 0;
}

.materials-table tbody tr:hover {
  background-color: #f5f5f5;
}

.selected-row {
  background-color: #e3f2fd !important;
}

.selected-row:hover {
  background-color: #bbdefb !important;
}

.table-container {
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 6px; /* 将字体大小从12px减小到6px */
}

.data-table th,
.data-table td {
  border: 1px solid #ddd;
  padding: 4px 2px; /* 减小内边距以适应更小的字体 */
  text-align: center;
}

.data-table th {
  background-color: #f2f2f2;
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table td:first-child {
  position: sticky;
  left: 0;
  background-color: #f2f2f2;
  z-index: 1;
  font-weight: bold;
  text-align: left;
}

.data-table tbody tr:hover {
  background-color: #f5f5f5;
}

.highlight-positive {
  background-color: rgba(76, 175, 80, 0.2);
}

.highlight-negative {
  background-color: rgba(244, 67, 54, 0.2);
}

.no-data {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #999;
  font-style: italic;
}

.response-json {
  background-color: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  font-family: monospace;
  white-space: pre-wrap;
  word-break: break-all;
  font-size: 14px;
  line-height: 1.5;
  color: #333;
  max-height: 100%;
  overflow: auto;
  display: none; /* 隐藏原始JSON显示 */
}

.highlight-negative {
  background-color: rgba(244, 67, 54, 0.2);
}

.clickable-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.clickable-row:hover {
  background-color: rgba(33, 150, 243, 0.1);
}

/* 添加Top10值表格样式 */
.top-values-container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  justify-content: space-between;
}

.top-values-section {
  flex: 1;
  min-width: 300px;
}

.top-values-section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 6px;
}

.top-values-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.top-values-table th,
.top-values-table td {
  border: 1px solid #ddd;
  padding: 6px;
  text-align: center;
}

.top-values-table th {
  background-color: #f2f2f2;
  font-weight: bold;
}

.top-values-table tr:hover {
  background-color: #f8f8f8;
}

/* 添加直方图样式 */
.chart-container {
  margin-bottom: 15px;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 10px;
  background-color: #fff;
}

.bar-chart {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.bar-label {
  width: 40%;
  text-align: right;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.bar {
  height: 20px;
  transition: width 0.3s;
  border-radius: 2px;
  position: relative;
}

.bar-value {
  position: absolute;
  right: -40px;
  top: 0;
  font-size: 12px;
  color: #333;
  width: 35px;
  text-align: right;
}

/* 修改样式使正负值分别向右和向左显示 */
.bar-item {
  display: flex;
  align-items: center;
  position: relative;
  cursor: pointer;
  height: 25px;
}

.bar-label {
  width: 40%;
  text-align: center;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  z-index: 2;
}

.bar {
  height: 20px;
  transition: width 0.3s;
  border-radius: 2px;
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
}

.bar-positive {
  left: 60%;
}

.bar-negative {
  right: 60%;
}

.bar-value {
  position: absolute;
  font-size: 12px;
  color: #333;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  text-align: left;
}

/* 语言切换按钮样式 */
.language-switch {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 10;
}

.language-switch {
  display: flex;
  justify-content: flex-end;
}

.language-button {
  background-color: rgba(255, 255, 255, 0.8);
  color: #333;
  border: 1px solid #ccc;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.language-button:hover {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.help-button {
  background-color: rgba(255, 255, 255, 0.8);
  color: #333;
  border: 1px solid #ccc;
  border-radius: 16px;
  padding: 6px 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-left: 10px;
}

.help-button:hover {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

/* 帮助面板样式 */
.help-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.help-panel {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.help-panel-header {
  padding: 12px 15px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.help-panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.help-panel-content {
  padding: 15px;
  overflow-y: auto;
  max-height: calc(90vh - 50px);
}

.chart-legend {
  margin-top: 10px;
  display: flex;
  flex-direction: row;
  gap: 15px;
  justify-content: center;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  display: inline-block;
}

.legend-text {
  font-size: 9px;
  color: #555;
}
</style>
