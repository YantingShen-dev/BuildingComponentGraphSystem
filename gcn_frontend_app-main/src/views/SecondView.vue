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
        <!-- 使用视频按钮组件 -->
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
            {{ currentLanguage === 'zh' ? '显示内墙面' : 'Show Internal Wall' }}
          </button>
          <button @click="toggleClippedFaces" class="mode-button" :class="{ 'active': !showIntersections && showClippedFaces }">
            {{ currentLanguage === 'zh' ? '显示外墙面' : 'Show External Wall' }}
          </button>
          <button @click="toggleAdjacencyMatrixDialog" class="full-width-button">
            {{ currentLanguage === 'zh' ? '显示邻接矩阵' : 'Show Adjacency Matrix' }}
          </button>
        </div>
      </div>
      <!-- 在底部添加导出表格按钮 -->
      <div class="export-button-container">
        <button @click="exportToExcel" class="export-button" :disabled="isLoading">
          <span v-if="isLoading" class="loading-spinner"></span>
          <span v-else>{{ currentLanguage === 'zh' ? '计算能耗' : 'Calculate Energy Consumption' }}</span>
        </button>
      </div>
      <div class="notch-container">
        <div class="notch">
          <span class="notch-text">{{ currentLanguage === 'zh' ? '第二步：模型分析' : 'Step 2: Model Analysis' }}</span>
        </div>
      </div>
    </div>
    <div class="right-container">
      <div class="right-panel upper-panel">
        <div class="notch-container upper-notch">
          <div class="notch">
            <span class="notch-text">{{ currentLanguage === 'zh' ? '修改平面' : 'Modify Plane' }}</span>
          </div>
        </div>
        <div class="panel-content">
          <canvas ref="upperCanvasRef" class="upper-canvas"></canvas>
          <!-- 添加绘制门窗按钮 -->
          <button
            class="draw-button"
            :class="{ 'active': isDrawingEnabled }"
            @click="isDrawingEnabled = !isDrawingEnabled"
          >
            {{ currentLanguage === 'zh' ? '绘制门窗' : 'Draw Windows and Doors' }}
          </button>
          <!-- 现有的侧边栏代码 -->
          <div class="upper-sidebar" :class="{ 'collapsed': !isSidebarExpanded }" v-if="currentSelectedGroupIndex !== null && currentSelectedGroupIndex >= 0 && currentSelectedGroupIndex < faceGroups.length">
            <div class="sidebar-toggle" @click="isSidebarExpanded = !isSidebarExpanded">
              <span class="toggle-arrow" :class="{ 'collapsed': !isSidebarExpanded }">{{ isSidebarExpanded ? '›' : '‹' }}</span>
            </div>
            <div class="sidebar-content" v-show="isSidebarExpanded">
              <h3>{{ currentLanguage === 'zh' ? '平面属性' : 'Plane Properties' }}</h3>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '序号' : 'No.' }}:</span>
                <span class="property-value">{{ currentSelectedGroupIndex + 1 }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '大类' : 'Type' }}:</span>
                <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].category }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '外接条件' : 'Out' }}:</span>
                <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].externalCondition }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '面积' : 'Area' }}:</span>
                <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].area.toFixed(2) }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '形状系数' : 'SI' }}:</span>
                <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].shapeCoefficient.toFixed(2) }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '子面类型系数' : 'SType' }}:</span>
                <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].subFaceTypeCoefficient }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '子面总面积' : 'SArea' }}:</span>
                <span class="property-value">{{ faceGroups[currentSelectedGroupIndex].subFaceTotalArea.toFixed(2) }}</span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '子面U值' : 'SCon' }}:</span>
                <span class="property-value">
                  {{ faceGroups[currentSelectedGroupIndex].subFaceUValue.toFixed(2) }}
                </span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '子面SHGC' : 'SSHGC' }}:</span>
                <span class="property-value">
                  {{ faceGroups[currentSelectedGroupIndex].subFaceSHGC.toFixed(2) }}
                </span>
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '导热系数' : 'Con' }}:</span>
                <input
                  type="number"
                  class="property-input"
                  :value="faceGroups[currentSelectedGroupIndex].conductivity"
                  min="0.1"
                  max="2"
                  step="0.1"
                  @input="updateConductivity($event)"
                />
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '厚度' : 'Thi' }}:</span>
                <input
                  type="number"
                  class="property-input"
                  :value="faceGroups[currentSelectedGroupIndex].thickness"
                  min="0.1"
                  max="0.5"
                  step="0.01"
                  @input="updateThickness($event)"
                />
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '长波辐射吸收比' : 'TA' }}:</span>
                <input
                  type="number"
                  class="property-input"
                  :value="faceGroups[currentSelectedGroupIndex].longwaveAbsorptance"
                  min="0"
                  max="1"
                  step="0.01"
                  @input="updateLongwaveAbsorptance($event)"
                />
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '太阳辐射吸收比' : 'SA' }}:</span>
                <input
                  type="number"
                  class="property-input"
                  :value="faceGroups[currentSelectedGroupIndex].solarAbsorptance"
                  min="0"
                  max="1"
                  step="0.01"
                  @input="updateSolarAbsorptance($event)"
                />
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '可见光辐射吸收比' : 'VA' }}:</span>
                <input
                  type="number"
                  class="property-input"
                  :value="faceGroups[currentSelectedGroupIndex].visibleAbsorptance"
                  min="0"
                  max="1"
                  step="0.01"
                  @input="updateVisibleAbsorptance($event)"
                />
              </div>
              <div class="property-item">
                <span class="property-label">{{ currentLanguage === 'zh' ? '朝向' : 'Dir' }}:</span>
                <span class="property-value">{{ currentLanguage === 'zh' ? faceGroups[currentSelectedGroupIndex].direction : faceGroups[currentSelectedGroupIndex].direction.replace('东', 'East').replace('南', 'South').replace('西', 'West').replace('北', 'North').replace('下', 'None').replace('上', 'None').replace('0', 'None') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="right-panel lower-panel">
        <div class="panel-content">
          <!-- 保留交集面和裁剪面组表格 -->
          <div class="face-groups-section">
            <div class="table-container">
              <table class="face-groups-table">
                <thead>
                  <tr>
                    <th>{{ currentLanguage === 'zh' ? '序号' : 'No.' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '大类' : 'Type' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '外接条件' : 'Out' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '面积' : 'Area' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '形状系数' : 'SI' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '子面类型系数' : 'SType' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '子面总面积' : 'SArea' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '子面U值' : 'SCon' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '子面SHGC' : 'SSHGC' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '导热系数' : 'Con' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '厚度' : 'Thi' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '长波辐射吸收比' : 'TA' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '太阳辐射吸收比' : 'SA' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '可见光辐射吸收比' : 'VA' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '朝向' : 'Dir' }}</th>
                    <th>{{ currentLanguage === 'zh' ? '操作' : 'Action' }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(group, index) in faceGroups" :key="index" :class="{ 'intersection-row': group.type === '交集面', 'clipped-row': group.type === '裁剪面组' }">
                    <td>{{ index + 1 }}</td>
                    <td>{{ group.category }}</td>
                    <td>{{ group.externalCondition }}</td>
                    <td>{{ group.area.toFixed(2) }}</td>
                    <td>{{ group.shapeCoefficient.toFixed(2) }}</td>
                    <td>{{ group.subFaceTypeCoefficient }}</td>
                    <td>{{ group.subFaceTotalArea.toFixed(2) }}</td>
                    <td>{{ group.subFaceUValue.toFixed(2) }}</td>
                    <td>{{ group.subFaceSHGC.toFixed(2) }}</td>
                    <td>{{ group.conductivity.toFixed(2) }}</td>
                    <td>{{ group.thickness.toFixed(2) }}</td>
                    <td>{{ group.longwaveAbsorptance.toFixed(2) }}</td>
                    <td>{{ group.solarAbsorptance.toFixed(2) }}</td>
                    <td>{{ group.visibleAbsorptance.toFixed(2) }}</td>
                    <td>{{ currentLanguage === 'zh' ? group.direction : group.direction.replace('东', 'East').replace('南', 'South').replace('西', 'West').replace('北', 'North').replace('下', 'None').replace('上', 'None').replace('0', 'None') }}</td>
                    <td>
                      <button class="action-button" @click="highlightGroup(index)">{{ currentLanguage === 'zh' ? '查看' : 'View' }}</button>
                    </td>
                  </tr>
                  <tr v-if="faceGroups.length === 0">
                    <td colspan="11" class="no-data">{{ currentLanguage === 'zh' ? '无数据' : 'No Data' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 邻接矩阵弹窗 -->
  <div v-if="showAdjacencyMatrixDialog" class="matrix-dialog-overlay" @click.self="closeAdjacencyMatrixDialog">
    <div class="matrix-dialog">
      <div class="matrix-dialog-header">
        <h3>{{ currentLanguage === 'zh' ? '构件邻接矩阵' : 'Component Adjacency Matrix' }}</h3>
        <button class="close-button" @click="closeAdjacencyMatrixDialog">×</button>
      </div>
      <div class="matrix-dialog-content">
        <div class="matrix-description">
          <p>{{ currentLanguage === 'zh' ? '邻接矩阵表示构件之间的连接关系：1表示连接，0表示不连接' : 'Adjacency matrix represents the connection relationship between components: 1 represents connection, 0 represents no connection' }}</p>
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

  <!-- 添加门窗信息提示 -->
  <div v-if="showWindowInfoTooltip && selectedWindowInfo"
       class="window-info-tooltip"
       :style="{left: windowInfoPosition.x + 'px', top: windowInfoPosition.y + 'px'}">
    <div class="window-info-content">
      <div class="window-info-item">
        <span class="window-info-label">{{ currentLanguage === 'zh' ? '类型' : 'Type' }}:</span>
        <div class="window-type-toggle">
          <button
            :class="['type-toggle-btn', editingWindowInfo.type === 'window' ? 'active' : '']"
            @click="setWindowType('window')"
          >{{ currentLanguage === 'zh' ? '窗' : 'Window' }}</button>
          <button
            :class="['type-toggle-btn', editingWindowInfo.type === 'door' ? 'active' : '']"
            @click="setWindowType('door')"
          >{{ currentLanguage === 'zh' ? '门' : 'Door' }}</button>
        </div>
      </div>
      <div class="window-info-item">
        <span class="window-info-label">{{ currentLanguage === 'zh' ? '长度' : 'Length' }}:</span>
        <input
          type="number"
          class="window-info-input"
          :value="Number(editingWindowInfo.width).toFixed(2)"
          @input="e => { editingWindowInfo.width = Number((e.target as HTMLInputElement).value); updateWindowDimensions(); }"
          step="0.01"
          min="0.1"
        />
      </div>
      <div class="window-info-item">
        <span class="window-info-label">{{ currentLanguage === 'zh' ? '宽度' : 'Width' }}:</span>
        <input
          type="number"
          class="window-info-input"
          :value="Number(editingWindowInfo.height).toFixed(2)"
          @input="e => { editingWindowInfo.height = Number((e.target as HTMLInputElement).value); updateWindowDimensions(); }"
          step="0.01"
          min="0.1"
        />
      </div>
      <div class="window-info-item">
        <span class="window-info-label">{{ currentLanguage === 'zh' ? '面积' : 'Area' }}:</span>
        <span class="window-info-value">{{ (editingWindowInfo.width * editingWindowInfo.height).toFixed(2) }}</span>
      </div>
      <div class="window-info-item">
        <span class="window-info-label">{{ currentLanguage === 'zh' ? 'U值' : 'U Value' }}:</span>
        <input
          type="number"
          class="window-info-input"
          :value="Number(editingWindowInfo.uValue).toFixed(2)"
          @input="e => { editingWindowInfo.uValue = Number((e.target as HTMLInputElement).value); updateWindowDimensions(); }"
          step="0.1"
          min="0.5"
          max="6"
        />
      </div>
      <div class="window-info-item">
        <span class="window-info-label">{{ currentLanguage === 'zh' ? 'SHGC值' : 'SHGC' }}:</span>
        <input
          v-if="editingWindowInfo.type === 'window'"
          type="number"
          class="window-info-input"
          :value="Number(editingWindowInfo.shgc).toFixed(2)"
          @input="e => { editingWindowInfo.shgc = Number((e.target as HTMLInputElement).value); updateWindowDimensions(); }"
          step="0.01"
          min="0"
          max="1"
        />
        <span v-else class="window-info-value">0</span>
      </div>
      <div class="window-info-action">
        <button class="window-delete-button" @click="deleteSelectedWindow">{{ currentLanguage === 'zh' ? '删除' : 'Delete' }}</button>
      </div>
    </div>
  </div>

  <!-- 添加属性解释面板 -->
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
import { ref, onMounted, onBeforeUnmount, nextTick, reactive, watch } from 'vue';
import VideoButton from '@/components/VideoButton.vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { useRouter } from 'vue-router';
import {
  CubeData,
  cubesToFaces,
  renderFacesInScene,
  Face,
  findAllFaceIntersections,
  computeAllClippedFaces,
  groupConnectedClippedFaces
} from '../utils/cubeToInterval';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

// 获取路由器实例
const router = useRouter();

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
    mesh3D?: THREE.Mesh | null; // 3D视图中的网格引用
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

// 添加加载状态变量
const isLoading = ref(false);

// 处理返回按钮点击
const handleBackButton = () => {
  // 显示确认弹窗
  if (window.confirm(currentLanguage.value === 'zh' ? '确定返回上一步吗？您已经建模好的立方体将被保留。绘制的门窗将被清除。' : 'Are you sure you want to go back? Your modeled cubes will be kept but any drawn windows and doors will be cleared.')) {
    // 清除面组数据，因为要重新建模
    localStorage.removeItem('faceGroupsData');
    console.log('返回页面1前已清除面组数据');

    // 用户确认后，导航回首页，并带上查询参数标记是从第二页返回的
    router.push('/?returnFromSecond=true');
  }
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
  console.log('第二页组件已挂载，初始化场景');

  // 监听浏览器关闭事件，清理数据
  window.addEventListener('beforeunload', handleBeforeUnload);

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

// 保存面组数据到localStorage
const saveFaceGroupsToStorage = () => {
  try {
    // 清理面组数据，排除不可序列化的mesh对象
    const cleanFaceGroups = faceGroups.value.map(group => ({
      ...group,
      windows: group.windows?.map(window => ({
        position: {
          x: window.position.x,
          y: window.position.y,
          z: window.position.z
        },
        width: window.width,
        height: window.height,
        type: window.type,
        uValue: window.uValue,
        shgc: window.shgc
        // 排除mesh和mesh3D属性
      })) || []
    }));
    localStorage.setItem('faceGroupsData', JSON.stringify(cleanFaceGroups));
    console.log('已保存面组数据到localStorage');
  } catch (error) {
    console.error('保存面组数据到localStorage失败:', error);
  }
};

// 从localStorage加载面组数据
const loadFaceGroupsFromStorage = () => {
  try {
    const savedFaceGroups = localStorage.getItem('faceGroupsData');
    if (savedFaceGroups) {
      const parsedFaceGroups = JSON.parse(savedFaceGroups);
      if (Array.isArray(parsedFaceGroups)) {
        // 转换门窗位置数据格式
        faceGroups.value = parsedFaceGroups.map(group => ({
          ...group,
          windows: group.windows?.map((window: any) => ({
            ...window,
            position: window.position.x !== undefined ?
              new THREE.Vector3(window.position.x, window.position.y, window.position.z) :
              window.position,
            mesh: null,
            mesh3D: null
          })) || []
        }));
        console.log('从localStorage成功加载面组数据，包含', faceGroups.value.length, '个面组');

        // 输出门窗信息用于调试
        faceGroups.value.forEach((group, index) => {
          if (group.windows && group.windows.length > 0) {
            console.log(`面组${index}包含${group.windows.length}个门窗`);
          }
        });

        // 渲染所有面组的门窗到3D视图 - 延迟100毫秒确保几何数据计算完成
        setTimeout(() => {
          renderAllWindowsTo3DView();
        }, 100);
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

  // 保存到localStorage
  saveFaceGroupsToStorage();
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
        // 释放几何体和材质资源
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
        return false; // 移除该门窗
      }
      return true; // 保留其他对象
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
    upperCamera.position.set(0, 4, 0);
    (upperCamera as any).up.set(0, 0, 1); // 旋转180度
    upperCamera.lookAt(0, 0, 0);
  } else if (normal.x > 0.9) { // 如果面朝向+x方向
    upperCamera.position.set(0, 4, 0);
    (upperCamera as any).up.set(-1, 0, 0); // 顺时针旋转90度
    upperCamera.lookAt(0, 0, 0);
  } else if (normal.x < -0.9) { // 如果面朝向-x方向
    upperCamera.position.set(0, 4, 0);
    (upperCamera as any).up.set(1, 0, 0); // 逆时针旋转90度
    upperCamera.lookAt(0, 0, 0);
  } else {
    upperCamera.position.set(0, 4, 0);
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

    // 同时将所有门窗反向渲染到3D视图中 - 延迟100毫秒确保几何数据计算完成
    setTimeout(() => {
      group.windows.forEach(windowData => {
        renderWindowTo3DView(windowData, group);
      });
    }, 100);
  }
};

// 高亮显示选中的面组
const highlightGroup = (groupIndex: number) => {
  // 先清除当前选择
  clearSelection();

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
  // const gridHelper = new THREE.GridHelper(10, 10);
  // upperScene.add(gridHelper);

  // const axesHelper = new THREE.AxesHelper(5);
  // upperScene.add(axesHelper);

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

      // 将门窗反向渲染到3D视图中 - 延迟100毫秒确保几何数据计算完成
      const currentGroup = faceGroups.value[currentSelectedGroupIndex.value];
      setTimeout(() => {
        renderWindowTo3DView(windowData, currentGroup);
      }, 100);
    } else {
      console.warn('未选中面组，无法关联门窗');
    }
  }
};

// 将门窗反向渲染到3D视图中
const renderWindowTo3DView = (windowData: any, faceGroup: FaceGroup) => {
  if (!scene || !faceGroup) return;

  console.log('开始将门窗反向渲染到3D视图', windowData, faceGroup);

  // 获取面组的法向量
  let normal: THREE.Vector3;
  if (faceGroup.type === '交集面') {
    const faceIndex = faceGroup.faceIndices[0];
    normal = intersectionFaces[faceIndex].normal.clone();
  } else {
    const faceIndex = faceGroup.faceIndices[0];
    normal = clippedFaces[faceIndex].normal.clone();
  }

  // 计算面组的中心点（与renderFaceGroupInUpperViewport中的逻辑一致）
  const center = new THREE.Vector3();
  faceGroup.vertices.forEach(v => {
    (center as any).add(v);
  });
  (center as any).divideScalar(faceGroup.vertices.length);

  // 获取门窗在右上角视口中的位置（相对于原点的位置）
  const upperViewportPos = windowData.position.clone();

  // 计算反向变换的四元数
  // 这是renderFaceGroupInUpperViewport中变换的逆变换
  const yAxis = new THREE.Vector3(0, 1, 0);
  const rotationAxis = new THREE.Vector3();
  (rotationAxis as any).crossVectors(normal, yAxis);

  let inverseQuaternion = new THREE.Quaternion();
  let angle = 0;
  if ((rotationAxis as any).length() > 0.001) {
    (rotationAxis as any).normalize();
    angle = Math.acos((normal as any).dot(yAxis));
    // 使用负角度进行反向旋转
    (inverseQuaternion as any).setFromAxisAngle(rotationAxis, -angle);
  }

  // 将右上角视口的2D位置转换回3D空间
  // 1. 首先创建一个在XZ平面上的3D位置（y=0）
  const localPos = new THREE.Vector3(upperViewportPos.x, 0, upperViewportPos.z);

  // 2. 应用反向旋转，将位置从XZ平面转换到原始面的方向
  (localPos as any).applyQuaternion(inverseQuaternion);

  // 3. 加上面组的中心点，得到最终的3D世界坐标
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

  // 设置位置
  mesh.position.copy(worldPos);

  // 设置旋转，使门窗与面平行
  // 门窗默认法向量是Z轴方向(0,0,1)，需要旋转到与面法向量平行
  const defaultNormal = new THREE.Vector3(0, 0, 1);
  const targetNormal = normal.clone();
  (targetNormal as any).normalize();

  // 计算从门窗默认法向量到面法向量的旋转
  const windowRotationAxis = new THREE.Vector3();
  (windowRotationAxis as any).crossVectors(defaultNormal, targetNormal);

  const windowQuaternion = new THREE.Quaternion();
  if ((windowRotationAxis as any).length() > 0.001) {
    (windowRotationAxis as any).normalize();
    const windowAngle = Math.acos((defaultNormal as any).dot(targetNormal));
    (windowQuaternion as any).setFromAxisAngle(windowRotationAxis, windowAngle);
  }

  // 应用旋转
  (mesh as any).quaternion.copy(windowQuaternion);

  // 对于南北朝向的面，需要额外绕X轴旋转90度
  if (Math.abs(targetNormal.x) > 0.9) { // 南方向(1,0,0)或北方向(-1,0,0)
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

  // 将3D网格引用保存到windowData中，方便后续管理
  windowData.mesh3D = mesh;

  console.log('门窗已成功渲染到3D视图', {
    originalPos: upperViewportPos,
    worldPos: worldPos,
    normal: normal,
    center: center
  });
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
    const windowToRemove = currentGroup.windows[windowIndex];

    // 从右上角视口场景中删除门窗
    if (upperScene && selectedWindowMesh.value) {
      upperScene.remove(selectedWindowMesh.value);

      // 如果有边框，也一并删除
      if (windowSelectionBorder) {
        upperScene.remove(windowSelectionBorder);
        windowSelectionBorder = null;
      }

      console.log('已从右上角视口场景中移除门窗对象');
    }

    // 从3D主场景中删除门窗
    if (scene && windowToRemove.mesh3D) {
      scene.remove(windowToRemove.mesh3D);
      console.log('已从3D主场景中移除门窗对象');
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
    // 保存到localStorage
    saveFaceGroupsToStorage();

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
    // 保存到localStorage
    saveFaceGroupsToStorage();

    // 更新选中窗口信息
    selectedWindowInfo.value = {
      width,
      height,
      area: width * height,
      type: editingWindowInfo.value.type,
      uValue: editingWindowInfo.value.uValue,
      shgc: editingWindowInfo.value.type === 'window' ? editingWindowInfo.value.shgc : 0
    };

    // 同时更新3D视图中的门窗
    if (windowData.mesh3D && scene) {
      // 先移除旧的3D门窗
      scene.remove(windowData.mesh3D);
    }
    // 重新渲染到3D视图
    renderWindowTo3DView(windowData, currentGroup);

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
    // 保存到localStorage
    saveFaceGroupsToStorage();

    // 更新选中窗口信息
    selectedWindowInfo.value = {
      width,
      height,
      area: width * height,
      type: editingWindowInfo.value.type,
      uValue: editingWindowInfo.value.uValue,
      shgc: editingWindowInfo.value.type === 'window' ? editingWindowInfo.value.shgc : 0
    };

    // 同时更新3D视图中的门窗
    if (windowData.mesh3D && scene) {
      // 先移除旧的3D门窗
      scene.remove(windowData.mesh3D);
    }
    // 重新渲染到3D视图
    renderWindowTo3DView(windowData, currentGroup);

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
    // 保存到localStorage
    saveFaceGroupsToStorage();

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
    // 保存到localStorage
    saveFaceGroupsToStorage();

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
    // 设置加载状态为true
    isLoading.value = true;

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

    // 保存面组数据到localStorage，包括门窗信息（排除不可序列化的mesh对象）
    const cleanFaceGroups = faceGroups.value.map(group => ({
      ...group,
      windows: group.windows?.map(window => ({
        position: {
          x: window.position.x,
          y: window.position.y,
          z: window.position.z
        },
        width: window.width,
        height: window.height,
        type: window.type,
        uValue: window.uValue,
        shgc: window.shgc
        // 排除mesh和mesh3D属性
      })) || []
    }));
    localStorage.setItem('faceGroupsData', JSON.stringify(cleanFaceGroups));
    console.log('已保存面组数据到localStorage，包含', cleanFaceGroups.length, '个面组');

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
  } finally {
    // 无论成功或失败，都重置加载状态
    isLoading.value = false;
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
        // 注意：这里只使用计算好的数值，不包含门窗的mesh对象
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
        explain: true  // 启用可解释性分析
      };

      // 发送POST请求到本地端口5000
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
      
      // 创建 AbortController 用于超时控制（5分钟超时）
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 300000); // 5分钟
      
      fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData),
        signal: controller.signal
      })
      .then(response => {
        clearTimeout(timeoutId); // 清除超时
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('JSON数据成功发送到本地服务器:', data);
        // 保存完整的响应数据
        resolve({
          success: true,
          message: data.message || "数据接收成功",
          data: data
        });
      })
      .catch(error => {
        clearTimeout(timeoutId); // 清除超时
        console.error('发送JSON数据到本地服务器失败:', error);
        let errorMessage = error.message;
        if (error.name === 'AbortError') {
          errorMessage = '请求超时（5分钟）。解释过程可能需要较长时间，请稍后重试。';
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

// 添加语言相关的响应式变量
const currentLanguage = ref('en'); // 默认英文

// 添加帮助面板状态
const showHelpPanel = ref(false);

// 切换帮助面板函数
const toggleHelpPanel = () => {
  showHelpPanel.value = !showHelpPanel.value;
  console.log('切换帮助面板', showHelpPanel.value);
};

// 切换语言函数
const toggleLanguage = () => {
  currentLanguage.value = currentLanguage.value === 'zh' ? 'en' : 'zh';
  console.log('语言已切换为:', currentLanguage.value);
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
  height: calc((95% - 2px) * 2/3);
  position: relative; /* 确保定位上下文正确 */
  overflow: hidden; /* 防止视口出现滚动条 */
}

.lower-panel {
  height: calc((95% - 2px) * 1/3);
  overflow: hidden; /* 防止视口出现滚动条 */
  position: relative; /* 确保定位上下文正确 */
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
  height: 100%;
  box-sizing: border-box;
  position: relative; /* 确保内容区域有正确的定位上下文 */
  overflow: hidden; /* 防止内容区域出现滚动条 */
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
}

.notch-text {
  font-size: 10px;
  font-weight: bold;
  letter-spacing: 0.5px;
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
  margin-top: 0; /* 移除顶部边距 */
  border-top: none; /* 移除顶部边框 */
  padding-top: 0; /* 移除顶部内边距 */
  height: 100%; /* 让区域填满整个视口 */
  display: flex;
  flex-direction: column;
}

.face-groups-section h3 {
  margin-top: 0;
  margin-bottom: 5px; /* 减少底部边距 */
  font-size: 7px; /* 将字体缩小一半 */
  color: #333;
}

.table-container {
  max-height: none; /* 移除最大高度限制 */
  height: 100%; /* 让表格容器填满可用空间 */
  overflow-y: auto;
  border: 1px solid #eee;
  border-radius: 4px;
  flex: 1; /* 让表格容器占据剩余空间 */
}

.face-groups-table {
  width: 100%;
  border-collapse: collapse;
}

.face-groups-table th, .face-groups-table td {
  border: 1px solid #ddd;
  padding: 3px 4px; /* 减小内边距 */
  text-align: left;
  font-size: 10px;
  white-space: nowrap; /* 防止文字换行 */
  max-width: 100px; /* 限制最大宽度 */
  overflow: hidden;
  text-overflow: ellipsis; /* 超出部分显示省略号 */
}

.face-groups-table th {
  background-color: #f2f2f2;
  font-weight: bold;
  position: sticky;
  top: 0;
  z-index: 10;
  height: 20px; /* 限制表头高度 */
  vertical-align: middle; /* 垂直居中 */
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
  padding: 6px;
  text-align: center;
  font-size: 14px;
  min-width: 40px;
  height: 40px;
}

.adjacency-matrix .index-cell {
  background-color: #f2f2f2;
  font-weight: bold;
  position: sticky;
  z-index: 2;
  min-width: 40px;
  width: 40px;
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
  overflow: hidden; /* 确保panel-content不会滚动 */
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
  width: 220px;
  display: flex;
  max-height: calc(100% - 20px); /* 限制最大高度 */
  overflow: hidden; /* 防止整个侧边栏溢出 */
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
  overflow-y: auto; /* 只在侧边栏内容区域允许垂直滚动 */
  max-height: 100%; /* 确保内容区域可以滚动 */
  scrollbar-width: thin; /* 使滚动条更细 */
  scrollbar-color: rgba(0,0,0,0.2) transparent; /* 自定义滚动条颜色 */
}

.sidebar-content::-webkit-scrollbar {
  width: 6px; /* 滚动条宽度 */
}

.sidebar-content::-webkit-scrollbar-thumb {
  background-color: rgba(0,0,0,0.2); /* 滚动条颜色 */
  border-radius: 3px; /* 滚动条圆角 */
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

.lower-panel .panel-content {
  padding: 10px; /* 减少内边距，让表格有更多空间 */
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;
}

/* 添加加载图标样式 */
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
  to { transform: rotate(360deg); }
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

/* 帮助按钮样式 */
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
  max-height: 70vh;
}

.property-explanation {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.property-explanation .property-item {
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

.property-explanation .property-name {
  font-size: 14px;
  line-height: 1.5;
}
</style>
