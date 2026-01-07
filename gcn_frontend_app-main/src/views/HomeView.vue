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
        <button @click="toggleLanguage" class="language-and-video-button">
          {{ currentLanguage === 'zh' ? '中' : 'EN' }}
        </button>
        <!-- 使用视频按钮组件 -->
        <VideoButton :currentLanguage="currentLanguage" :defaultShow="true" />
      </div>

      <div class="controls">
        <button @click="createCube" class="create-button">
          {{ currentLanguage === 'zh' ? '手动创建立方体' : 'Create Cube Manually' }}
        </button>
        <div class="tutorial-panel">
          <div class="tutorial-header">
            <span class="header-text">
              {{ currentLanguage === 'zh' ? '使用教程' : 'Usage Tutorial' }}
            </span>
            <button @click="toggleTutorial" class="toggle-button">
              {{ showTutorial ? (currentLanguage === 'zh' ? '隐藏' : 'Hide') : (currentLanguage === 'zh' ? '显示' : 'Show') }}
            </button>
          </div>
          <div class="tutorial-content" v-if="showTutorial">
            <div class="tutorial-item">
              <div class="tutorial-icon">🖱️</div>
              <div class="tutorial-text">
                <strong>{{ currentLanguage === 'zh' ? '选择操作：' : 'Select Operation:' }}</strong>
                {{ currentLanguage === 'zh' ? '左键点击立方体，显示控制点和属性' : 'Left-click on the cube to display control points and properties' }}
              </div>
            </div>
            <div class="tutorial-item">
              <div class="tutorial-icon">↔️</div>
              <div class="tutorial-text">
                <strong>{{ currentLanguage === 'zh' ? '缩放操作：' : 'Scale Operation:' }}</strong>
                {{ currentLanguage === 'zh' ? '拖动红色控制点调整大小' : 'Drag the red control point to adjust the size' }}
              </div>
            </div>
            <div class="tutorial-item">
              <div class="tutorial-icon">✋</div>
              <div class="tutorial-text">
                <strong>{{ currentLanguage === 'zh' ? '移动操作：' : 'Move Operation:' }}</strong>
                {{ currentLanguage === 'zh' ? '拖动底部绿色控制点平移立方体' : 'Drag the bottom green control point to move the cube' }}
              </div>
            </div>
            <div class="tutorial-item">
              <div class="tutorial-icon">🔄</div>
              <div class="tutorial-text">
                <strong>{{ currentLanguage === 'zh' ? '视角控制：' : 'View Control:' }}</strong>
                {{ currentLanguage === 'zh' ? '右键旋转，中键平移，滚轮缩放视图' : 'Right-click to rotate, middle-click to pan, scroll to zoom' }}
              </div>
            </div>
            <div class="tutorial-item">
              <div class="tutorial-icon">🧲</div>
              <div class="tutorial-text">
                <strong>{{ currentLanguage === 'zh' ? '吸附功能：' : 'Adhesion Function:' }}</strong>
                {{ currentLanguage === 'zh' ? '立方体靠近时自动对齐面或角点' : 'The cube will automatically align with the face or corner when it is close' }}
              </div>
            </div>
            <div class="tutorial-item">
              <div class="tutorial-icon">📏</div>
              <div class="tutorial-text">
                <strong>{{ currentLanguage === 'zh' ? '精确调整：' : 'Accurate Adjustment:' }}</strong>
                {{ currentLanguage === 'zh' ? '使用右侧面板精确设置尺寸和位置' : 'Use the right panel to accurately set the size and position' }}
              </div>
            </div>
            <div class="tutorial-item">
              <div class="tutorial-icon">🗑️</div>
              <div class="tutorial-text">
                <strong>{{ currentLanguage === 'zh' ? '删除操作：' : 'Delete Operation:' }}</strong>
                {{ currentLanguage === 'zh' ? '点击右侧面板的删除按钮移除立方体' : 'Click the delete button in the right panel to remove the cube' }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="notch-container">
        <div class="notch">
          <span class="notch-text">{{ currentLanguage === 'zh' ? '第一步：建立模型' : 'Step 1: Build the Model' }}</span>
        </div>
      </div>

      <!-- 添加底部完成按钮 -->
      <div class="complete-button-container">
        <button @click="checkAndCompleteCubeModeling" class="complete-button">
          <span class="complete-icon">✓</span> {{ currentLanguage === 'zh' ? '完成体块建模' : 'Complete Cube Modeling' }}
        </button>
      </div>

      <!-- 添加侧边栏 -->
      <div class="sidebar" :class="{ 'sidebar-visible': showSidebar }">
        <div class="sidebar-header">
          <span class="header-text">{{ currentLanguage === 'zh' ? '立方体属性' : 'Cube Properties' }}</span>
        </div>
        <div class="sidebar-content">
          <div class="property-group">
            <div class="property-title">{{ currentLanguage === 'zh' ? '尺寸' : 'Size' }}</div>
            <div class="property-row">
              <div class="property-label">{{ currentLanguage === 'zh' ? '宽度 (X)(m):' : 'Width (X)(m):' }}</div>
              <div class="property-input">
                <input
                  type="number"
                  v-model.number="editableCubeSize.x"
                  @input="updateCubeSize"
                  step="0.1"
                  min="0.1"
                  class="size-input"
                />
              </div>
            </div>
            <div class="property-row">
              <div class="property-label">{{ currentLanguage === 'zh' ? '深度 (Y)(m):' : 'Depth (Y)(m):' }}</div>
              <div class="property-input">
                <input
                  type="number"
                  v-model.number="editableCubeSize.z"
                  @input="updateCubeSize"
                  step="0.1"
                  min="0.1"
                  class="size-input"
                />
              </div>
            </div>
            <div class="property-row">
              <div class="property-label">{{ currentLanguage === 'zh' ? '高度 (Z)(m):' : 'Height (Z)(m):' }}</div>
              <div class="property-input">
                <input
                  type="number"
                  v-model.number="editableCubeSize.y"
                  @input="updateCubeSize"
                  step="0.1"
                  min="0.1"
                  class="size-input"
                />
              </div>
            </div>
          </div>

          <div class="property-group">
            <div class="property-title">{{ currentLanguage === 'zh' ? '位置' : 'Position' }}</div>
            <div class="property-row">
              <div class="property-label">{{ currentLanguage === 'zh' ? 'X 坐标(m):' : 'X Coordinate(m):' }}</div>
              <div class="property-input">
                <input
                  type="number"
                  v-model.number="editableCubePosition.x"
                  @input="updateCubePosition"
                  step="0.1"
                  class="size-input"
                />
              </div>
            </div>
            <div class="property-row">
              <div class="property-label">{{ currentLanguage === 'zh' ? 'Y 坐标(m):' : 'Y Coordinate(m):' }}</div>
              <div class="property-input">
                <input
                  type="number"
                  v-model.number="editableCubePosition.z"
                  @input="updateCubePosition"
                  step="0.1"
                  class="size-input"
                />
              </div>
            </div>
            <div class="property-row">
              <div class="property-label">{{ currentLanguage === 'zh' ? 'Z 坐标(m):' : 'Z Coordinate(m):' }}</div>
              <div class="property-value">{{ cubePosition.y.toFixed(2) }}</div>
            </div>
          </div>

          <div class="delete-button-container">
            <button @click="deleteCube" class="delete-button">
              <span class="delete-icon">🗑️</span> {{ currentLanguage === 'zh' ? '删除立方体' : 'Delete Cube' }}
            </button>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, reactive, watch } from 'vue';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import {
  extractCubesData,
  cubesToIntervals,
  intervalsIntersect,
  intervalsAreDisjoint,
  areAllCubesConnected,
  findDisconnectedGroups
} from '@/utils/cubeToInterval';
import { useRouter } from 'vue-router';
import VideoButton from '@/components/VideoButton.vue';

// 获取路由器实例
const router = useRouter();

// 教程面板显示状态
const showTutorial = ref(true);

// 切换教程面板显示/隐藏
const toggleTutorial = () => {
  showTutorial.value = !showTutorial.value;
};

// 侧边栏显示状态
const showSidebar = ref(false);

// 立方体尺寸和位置
const cubeSize = reactive({ x: 0, y: 0, z: 0 });
const cubePosition = reactive({ x: 0, y: 0, z: 0 });

// 可编辑的立方体尺寸和位置（用于输入框）
const editableCubeSize = reactive({ x: 0, y: 0, z: 0 });
const editableCubePosition = reactive({ x: 0, z: 0 });

// 更新立方体尺寸
const updateCubeSize = () => {
  if (!selectedCube) return;

  // 确保尺寸不小于0.1
  editableCubeSize.x = Math.max(0.1, editableCubeSize.x);
  editableCubeSize.y = Math.max(0.1, editableCubeSize.y);
  editableCubeSize.z = Math.max(0.1, editableCubeSize.z);

  // 保存原始尺寸和位置
  const oldGeometry = selectedCube.geometry as THREE.BoxGeometry;
  const oldSize = new THREE.Vector3();
  if (oldGeometry.boundingBox === null) {
    oldGeometry.computeBoundingBox();
  }
  oldGeometry.boundingBox?.getSize(oldSize);

  // 记录原始高度和当前位置
  const oldHeight = oldSize.y;
  const oldPosition = selectedCube.position.clone();

  // 创建新的几何体
  const newGeometry = new THREE.BoxGeometry(
    editableCubeSize.x,
    editableCubeSize.y,
    editableCubeSize.z
  );

  // 替换几何体
  (selectedCube.geometry as any).dispose(); // 释放旧几何体
  selectedCube.geometry = newGeometry;

  // 更新边框
  // 移除旧边框
  const edgesToRemove: THREE.Object3D[] = [];
  selectedCube.children.forEach(child => {
    if (child instanceof THREE.LineSegments) {
      edgesToRemove.push(child);
    }
  });
  edgesToRemove.forEach(edge => {
    selectedCube?.remove(edge);
  });

  // 添加新边框
  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(newGeometry),
    new THREE.LineBasicMaterial({ color: 0x000000 })
  );
  selectedCube.add(edges);

  // 更新原始尺寸
  selectedCube.userData.originalScale = new THREE.Vector3(
    editableCubeSize.x,
    editableCubeSize.y,
    editableCubeSize.z
  );

  // 调整立方体位置，使底面保持在地平面上
  // 计算高度差的一半，因为立方体的原点在中心
  const heightDifference = (editableCubeSize.y - oldHeight) / 2;
  // 更新Y轴位置，保持底面在地平面上
  selectedCube.position.y = oldPosition.y + heightDifference;

  // 更新控制点位置
  updateAllControlPointsPositions(selectedCube);

  // 同步到cubeSize
  cubeSize.x = editableCubeSize.x;
  cubeSize.y = editableCubeSize.y;
  cubeSize.z = editableCubeSize.z;

  // 更新位置信息
  cubePosition.x = selectedCube.position.x;
  cubePosition.y = selectedCube.position.y;
  cubePosition.z = selectedCube.position.z;
};

// 更新立方体位置
const updateCubePosition = () => {
  if (!selectedCube) return;

  // 更新立方体位置 - 只修改X和Z坐标，保持Y坐标不变
  selectedCube.position.x = editableCubePosition.x;
  selectedCube.position.z = editableCubePosition.z;

  // 更新位置信息
  cubePosition.x = selectedCube.position.x;
  cubePosition.z = selectedCube.position.z;

  // 更新控制点位置
  updateAllControlPointsPositions(selectedCube);
};

// 删除当前选中的立方体
const deleteCube = () => {
  if (selectedCube) {
    // 从场景中移除立方体
    scene.remove(selectedCube);

    // 清空选中状态
    selectedCube = null;
    selectedControlPoint = null;

    // 隐藏侧边栏
    showSidebar.value = false;
  }
};

// 更新立方体属性信息
const updateCubeProperties = () => {
  if (selectedCube) {
    // 更新尺寸信息
    const geometry = selectedCube.geometry as THREE.BoxGeometry;
    const size = new THREE.Vector3();
    if (geometry.boundingBox === null) {
      geometry.computeBoundingBox();
    }
    geometry.boundingBox?.getSize(size);

    // 考虑缩放因素
    cubeSize.x = size.x * (selectedCube as any).scale.x;
    cubeSize.y = size.y * (selectedCube as any).scale.y;
    cubeSize.z = size.z * (selectedCube as any).scale.z;

    // 同步到可编辑尺寸
    editableCubeSize.x = parseFloat(cubeSize.x.toFixed(2));
    editableCubeSize.y = parseFloat(cubeSize.y.toFixed(2));
    editableCubeSize.z = parseFloat(cubeSize.z.toFixed(2));

    // 更新位置信息
    cubePosition.x = selectedCube.position.x;
    cubePosition.y = selectedCube.position.y;
    cubePosition.z = selectedCube.position.z;

    // 同步到可编辑位置
    editableCubePosition.x = parseFloat(cubePosition.x.toFixed(2));
    editableCubePosition.z = parseFloat(cubePosition.z.toFixed(2));

    // 显示侧边栏
    showSidebar.value = true;
  }
};

// 场景相关变量
const canvasRef = ref<HTMLCanvasElement | null>(null);
let scene: THREE.Scene;
let camera: THREE.PerspectiveCamera;
let renderer: THREE.WebGLRenderer;
let orbitControls: OrbitControls;
let raycaster: THREE.Raycaster;
let mouse: THREE.Vector2;
// 添加鼠标客户端坐标变量
let mouseClientPosition = { x: 0, y: 0 };
let selectedCube: THREE.Mesh | null = null;
let selectedControlPoint: THREE.Mesh | null = null;
// 控制点相关变量
let controlPointNormal = new THREE.Vector3(); // 控制点所在平面的法向量
let controlPointOriginalPosition = new THREE.Vector3(); // 控制点的原始位置

// 拖动线段相关变量
let isDragging = false;
let dragStartPoint = new THREE.Vector3();
let dragLine: any = null; // 使用any类型避免Line类型错误

// 添加移动系数变量
const MOVEMENT_SCALE = 1; // 控制点移动系数，可以根据需要调整

// 添加吸附相关常量
const SNAP_THRESHOLD = 0.12; // 吸附阈值，当两个立方体面之间的距离小于此值时触发吸附
const SNAP_HIGHLIGHT_COLOR = 0x00ffff; // 吸附高亮颜色
const SNAP_OFFSET = 0.2; // 吸附偏移量，用于微调曼哈顿距离阈值
const CORNER_SNAP_THRESHOLD = 0.12; // 角点吸附阈值，当两个立方体角点之间的距离小于此值时触发吸附

// 添加语言相关的响应式变量
const currentLanguage = ref('en'); // 默认英文


// 切换语言函数
const toggleLanguage = () => {
  currentLanguage.value = currentLanguage.value === 'zh' ? 'en' : 'zh';
  console.log('语言已切换为:', currentLanguage.value);
};

// 创建立方体
const createCube = () => {
  // 创建立方体几何体
  const geometry = new THREE.BoxGeometry(1, 1, 1);

  // 创建材质
  const material = new THREE.MeshStandardMaterial({
    color: 0x00aaff,
    transparent: true,
    opacity: 0.7
  });

  // 创建网格
  const cube = new THREE.Mesh(geometry, material);

  // 随机位置
  cube.position.set(
    Math.random() * 6 - 3,
    0.5,
    Math.random() * 6 - 3
  );

  // 添加到场景
  scene.add(cube);

  // 添加边框
  const edges = new THREE.LineSegments(
    new THREE.EdgesGeometry(geometry),
    new THREE.LineBasicMaterial({ color: 0x000000 })
  );
  cube.add(edges);

  console.log('立方体已创建');
};

// 创建控制点
const createControlPoints = (cube: THREE.Mesh) => {
  // 如果已经有控制点，先移除
  removeControlPoints();

  // 获取立方体的尺寸
  const geometry = cube.geometry as THREE.BoxGeometry;
  const size = new THREE.Vector3();
  if (geometry.boundingBox === null) {
    geometry.computeBoundingBox();
  }
  geometry.boundingBox?.getSize(size);

  // 控制点的位置（相对于立方体中心）
  const halfSize = size.clone().multiplyScalar(0.5);
  const positions = [
    new THREE.Vector3(0, halfSize.y, 0),  // 上
    new THREE.Vector3(halfSize.x, 0, 0),  // 右
    new THREE.Vector3(0, 0, halfSize.z),  // 前
    new THREE.Vector3(-halfSize.x, 0, 0), // 左
    new THREE.Vector3(0, 0, -halfSize.z), // 后
    new THREE.Vector3(0, -halfSize.y, 0)  // 底部（用于平移）- 确保在底面中心
  ];

  // 控制点的法向量（与位置方向相同，归一化）
  const normals = [
    new THREE.Vector3(0, 1, 0),   // 上
    new THREE.Vector3(1, 0, 0),   // 右
    new THREE.Vector3(0, 0, 1),   // 前
    new THREE.Vector3(-1, 0, 0),  // 左
    new THREE.Vector3(0, 0, -1),  // 后
    new THREE.Vector3(0, -1, 0)   // 底部（用于平移）
  ];

  // 创建控制点
  positions.forEach((position, index) => {
    // 创建控制点几何体
    const pointGeometry = new THREE.SphereGeometry(0.1, 16, 16);
    // 底部控制点使用不同颜色
    const pointColor = index === 5 ? 0x00ff00 : 0xff0000; // 底部控制点使用绿色
    const pointMaterial = new THREE.MeshBasicMaterial({ color: pointColor });
    const point = new THREE.Mesh(pointGeometry, pointMaterial);

    // 设置控制点位置
    point.position.copy(position);

    // 添加用户数据，用于标识控制点
    point.userData.isControlPoint = true;
    point.userData.normal = normals[index]; // 存储法向量
    point.userData.isTranslationControl = index === 5; // 标记底部控制点为平移控制点

    // 将控制点添加到立方体上
    cube.add(point);
  });

  // 将立方体设为选中状态
  selectedCube = cube;

  // 更新立方体属性信息
  updateCubeProperties();
};

// 移除控制点
const removeControlPoints = () => {
  // 如果有选中的立方体，从立方体上移除所有控制点
  if (selectedCube) {
    // 创建一个数组来存储要移除的控制点
    const pointsToRemove: THREE.Object3D[] = [];

    // 找出所有控制点
    selectedCube.children.forEach(child => {
      if (child instanceof THREE.Mesh && child.geometry instanceof THREE.SphereGeometry) {
        pointsToRemove.push(child);
      }
    });

    // 移除所有控制点
    pointsToRemove.forEach(point => {
      selectedCube?.remove(point);
    });

    // 确保将selectedCube设置为null，这样侧边栏会消失
    selectedCube = null;
    selectedControlPoint = null;

    // 隐藏侧边栏
    showSidebar.value = false;
  }
};

// 重置控制点颜色
const resetControlPointsColor = () => {
  if (selectedCube) {
    selectedCube.children.forEach(child => {
      if (child instanceof THREE.Mesh && child.geometry instanceof THREE.SphereGeometry) {
        const material = child.material as THREE.MeshBasicMaterial;
        // 检查是否是平移控制点（底部控制点）
        if (child.userData.isTranslationControl) {
          material.color.set(0x00ff00); // 绿色
        } else {
          material.color.set(0xff0000); // 红色
        }
      }
    });
  }
};

// 创建拖动线段
const createDragLine = (startPoint: THREE.Vector3) => {
  // 如果已经有线段，先移除
  removeDragLine();

  // 创建线段几何体（起点和终点相同）
  const points = [startPoint, startPoint.clone()];
  const geometry = new THREE.BufferGeometry();

  // 使用类型断言
  (geometry as any).setAttribute(
    'position',
    new (THREE as any).Float32BufferAttribute(
      [
        startPoint.x, startPoint.y, startPoint.z,
        startPoint.x, startPoint.y, startPoint.z
      ],
      3
    )
  );

  // 创建线段材质
  const material = new THREE.LineBasicMaterial({
    color: 0x00ff00,
    linewidth: 2
  });

  // 创建线段，使用类型断言
  dragLine = new (THREE as any).Line(geometry, material);

  // 添加到场景
  scene.add(dragLine);
};

// 更新拖动线段
const updateDragLine = (endPoint: THREE.Vector3) => {
  if (dragLine) {
    // 获取线段几何体
    const geometry = dragLine.geometry;
    const positionAttribute = geometry.getAttribute('position') as any;

    // 更新终点位置
    positionAttribute.setXYZ(1, endPoint.x, endPoint.y, endPoint.z);
    positionAttribute.needsUpdate = true;
  }
};

// 移除拖动线段
const removeDragLine = () => {
  if (dragLine) {
    scene.remove(dragLine);
    dragLine = null;
  }
};

// 处理鼠标点击事件
const onMouseDown = (event: MouseEvent) => {
  // 只处理鼠标左键点击
  if (event.button !== 0) return;

  // 计算鼠标在归一化设备坐标中的位置
  if (!canvasRef.value) return;

  const rect = canvasRef.value.getBoundingClientRect();
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

  // 更新射线
  raycaster.setFromCamera(mouse, camera);

  // 获取射线与场景中物体的交点
  const intersects = raycaster.intersectObjects(scene.children, true);

  // 检查是否点击了控制点
  let hitControlPoint = false;

  for (let i = 0; i < intersects.length; i++) {
    const intersect = intersects[i];
    const object = intersect.object;

    // 检查是否是控制点
    if (object instanceof THREE.Mesh &&
        object.geometry instanceof THREE.SphereGeometry &&
        object.userData.isControlPoint) {

      // 先重置所有控制点的颜色
      resetControlPointsColor();

      // 设置当前点击的控制点为黄色
      const material = object.material as THREE.MeshBasicMaterial;
      material.color.set(0xffff00); // 黄色

      selectedControlPoint = object;
      hitControlPoint = true;

      // 开始拖动
      isDragging = true;

      // 获取控制点的世界坐标（用于参考，不再作为线段起点）
      const controlPointWorldPos = new THREE.Vector3();
      (object as any).getWorldPosition(controlPointWorldPos);

      // 检查是否是平移控制点
      if (object.userData.isTranslationControl) {
        // 创建一个XY平面（Y=0平面）用于平移
        const xyPlane = new (THREE as any).Plane(new THREE.Vector3(0, 1, 0), 0);

        // 计算射线与XY平面的交点
        dragStartPoint = new THREE.Vector3();
        (raycaster as any).ray.intersectPlane(xyPlane, dragStartPoint);

        // 创建拖动线段
        createDragLine(dragStartPoint);

        // 禁用轨道控制器，防止拖动时旋转场景
        orbitControls.enabled = false;

        break;
      }

      // 保存控制点的法向量（需要转换到世界坐标系）
      controlPointNormal = object.userData.normal.clone();
      // 将法向量从局部坐标系转换到世界坐标系
      if (selectedCube) {
        const normalMatrix = new (THREE as any).Matrix3().getNormalMatrix((selectedCube as any).matrixWorld);
        (controlPointNormal as any).applyMatrix3(normalMatrix);
        (controlPointNormal as any).normalize();
      }

      // 保存控制点的原始位置
      controlPointOriginalPosition = object.position.clone();

      // 计算摄像机视屏面上的点作为线段起点
      // 使用当前鼠标位置对应的屏幕点作为起点
      // 创建一个平面，与摄像机视线垂直
      const cameraNormal = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
      const screenPlane = new (THREE as any).Plane(cameraNormal, 0);

      // 将平面移动到控制点位置
      (selectedControlPoint as any).getWorldPosition(controlPointWorldPos);
      const distanceToCamera = (controlPointWorldPos as any).distanceTo(camera.position);
      screenPlane.constant = -distanceToCamera;

      // 计算射线与平面的交点
      dragStartPoint = new THREE.Vector3();
      (raycaster as any).ray.intersectPlane(screenPlane, dragStartPoint);

      // 创建拖动线段
      createDragLine(dragStartPoint);

      // 禁用轨道控制器，防止拖动时旋转场景
      orbitControls.enabled = false;

      break;
    }
  }

  // 如果没有点击控制点，则检查是否点击了立方体
  if (!hitControlPoint) {
    // 检查是否点击了立方体
    let hitCube = false;
    let cubeToSelect: THREE.Mesh | null = null;

    // 首先检查是否点击了任何物体
    if (intersects.length > 0) {
      for (let i = 0; i < intersects.length; i++) {
        const intersect = intersects[i];

        // 确保有面索引，这表示确实击中了立方体的面
        if (intersect.faceIndex === undefined) {
          continue;
        }

        let object = intersect.object;

        // 如果点击的是立方体的边缘，需要找到其父对象（立方体）
        let foundCube = false;
        let currentObj = object;

        while (currentObj.parent && !foundCube) {
          if (currentObj instanceof THREE.Mesh && currentObj.geometry instanceof THREE.BoxGeometry) {
            foundCube = true;
            break;
          }
          currentObj = currentObj.parent;
        }

        // 如果找到了立方体
        if (foundCube && currentObj instanceof THREE.Mesh && currentObj.geometry instanceof THREE.BoxGeometry) {
          hitCube = true;
          cubeToSelect = currentObj;
          break;
        }
      }
    }

    // 如果点击了立方体，显示控制点
    if (hitCube && cubeToSelect) {
      createControlPoints(cubeToSelect);
    } else {
      // 如果没有点击到立方体，移除控制点
      removeControlPoints();
    }
  }
};

// 处理鼠标移动事件
const onMouseMove = (event: MouseEvent) => {
  // 如果没有在拖动，直接返回
  if (!isDragging || !selectedControlPoint) return;

  // 存储鼠标的客户端坐标，用于在动画循环中计算
  mouseClientPosition.x = event.clientX;
  mouseClientPosition.y = event.clientY;

  // 直接在鼠标移动事件中更新控制点位置，而不是等待动画循环
  if (canvasRef.value) {
    const rect = canvasRef.value.getBoundingClientRect();
    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    // 更新射线
    raycaster.setFromCamera(mouse, camera);

    // 检查是否是平移控制点
    if (selectedControlPoint.userData.isTranslationControl) {
      // 创建一个XY平面（Y=0平面）用于平移
      const xyPlane = new (THREE as any).Plane(new THREE.Vector3(0, 1, 0), 0);

      // 计算射线与XY平面的交点
      const targetPoint = new THREE.Vector3();
      (raycaster as any).ray.intersectPlane(xyPlane, targetPoint);

      // 更新拖动线段
      updateDragLine(targetPoint);

      // 计算移动向量（从起点到终点）
      const moveVector = new THREE.Vector3();
      (moveVector as any).subVectors(targetPoint, dragStartPoint);

      // 只保留XZ平面上的移动（Y轴保持不变）
      moveVector.y = 0;

      // 如果是第一次移动，保存立方体的原始位置
      if (!selectedCube?.userData.originalPosition) {
        selectedCube!.userData.originalPosition = selectedCube!.position.clone();
      }

      // 更新立方体位置 - 只移动X和Z坐标，保持Y坐标不变
      const newPosition = selectedCube!.userData.originalPosition.clone();
      newPosition.x += moveVector.x;
      newPosition.z += moveVector.z;
      // 保持Y坐标不变
      selectedCube!.position.set(newPosition.x, selectedCube!.position.y, newPosition.z);

      // 检查是否需要吸附到其他立方体
      checkAndSnapToCubes();

      // 更新所有控制点的位置
      updateAllControlPointsPositions(selectedCube!);

      // 更新立方体属性信息，使侧边栏实时显示最新的位置坐标
      updateCubeProperties();

      return; // 平移控制点处理完毕，不执行后续缩放逻辑
    }

    // 以下是原有的控制点处理逻辑（缩放）
    // 计算摄像机视屏面上的点作为线段终点
    const cameraNormal = new THREE.Vector3(0, 0, -1).applyQuaternion(camera.quaternion);
    const screenPlane = new (THREE as any).Plane(cameraNormal, 0);

    // 调整平面距离，使其更接近控制点的位置
    const controlPointWorldPos = new THREE.Vector3();
    (selectedControlPoint as any).getWorldPosition(controlPointWorldPos);
    const distanceToCamera = (controlPointWorldPos as any).distanceTo(camera.position);
    screenPlane.constant = -distanceToCamera;

    // 计算射线与平面的交点
    const targetPoint = new THREE.Vector3();
    (raycaster as any).ray.intersectPlane(screenPlane, targetPoint);

    // 更新拖动线段
    updateDragLine(targetPoint);

    // 计算线段向量（从起点到终点）
    const lineVector = new THREE.Vector3();
    (lineVector as any).subVectors(targetPoint, dragStartPoint);

    // 计算线段在控制点法向量上的投影长度
    const projectionLength = (lineVector as any).dot(controlPointNormal);

    // 添加移动系数，使控制点移动更加平滑
    const movementScale = MOVEMENT_SCALE; // 移动系数，可以根据需要调整

    // 更新控制点位置 - 沿法向移动投影长度的距离，并乘以移动系数
    if (selectedControlPoint) {
      // 同时移动立方体
      if (selectedCube) {
        // 计算立方体应该移动的距离向量
        const moveVector = controlPointNormal.clone().multiplyScalar(projectionLength * movementScale * 0.5);

        // 如果是第一次移动，保存立方体的原始位置
        if (!selectedCube.userData.originalPosition) {
          selectedCube.userData.originalPosition = selectedCube.position.clone();
        }

        // 更新立方体位置
        selectedCube.position.copy(selectedCube.userData.originalPosition);
        (selectedCube.position as any).add(moveVector);

        // 在移动方向上缩放立方体
        const geometry = selectedCube.geometry as THREE.BoxGeometry;
        const size = new THREE.Vector3();
        if (geometry.boundingBox === null) {
          geometry.computeBoundingBox();
        }
        geometry.boundingBox?.getSize(size);

        // 保存原始尺寸
        if (!selectedCube.userData.originalScale) {
          selectedCube.userData.originalScale = size.clone();
        }

        // 根据法向量确定要缩放的轴
        const normal = selectedControlPoint.userData.normal as THREE.Vector3;
        const scaleValue = Math.abs(projectionLength * movementScale);

        // 创建新的缩放向量，初始为1,1,1
        const newScale = new THREE.Vector3(1, 1, 1);

        // 根据法向量方向确定缩放轴
        if (normal.y === 1 || normal.y === -1) { // 上/下
          // 计算新的Y轴缩放值
          const originalHeight = (selectedCube.userData.originalScale as THREE.Vector3).y;
          // 将scaleValue除以立方体在Y方向的尺寸进行归一化
          const normalizedScaleValue = scaleValue / originalHeight;
          const scaleFactor = projectionLength > 0 ? 1 + normalizedScaleValue : Math.max(0.1, 1 - normalizedScaleValue);
          newScale.y = scaleFactor;
        } else if (normal.x === 1 || normal.x === -1) { // 右/左
          // 计算新的X轴缩放值
          const originalWidth = (selectedCube.userData.originalScale as THREE.Vector3).x;
          // 将scaleValue除以立方体在X方向的尺寸进行归一化
          const normalizedScaleValue = scaleValue / originalWidth;
          const scaleFactor = projectionLength > 0 ? 1 + normalizedScaleValue : Math.max(0.1, 1 - normalizedScaleValue);
          newScale.x = scaleFactor;
        } else if (normal.z === 1 || normal.z === -1) { // 前/后
          // 计算新的Z轴缩放值
          const originalDepth = (selectedCube.userData.originalScale as THREE.Vector3).z;
          // 将scaleValue除以立方体在Z方向的尺寸进行归一化
          const normalizedScaleValue = scaleValue / originalDepth;
          const scaleFactor = projectionLength > 0 ? 1 + normalizedScaleValue : Math.max(0.1, 1 - normalizedScaleValue);
          newScale.z = scaleFactor;
        }

        // 应用缩放
        (selectedCube as any).scale.copy(newScale);

        // 更新所有控制点的位置，包括当前正在拖动的控制点
        updateAllControlPointsPositions(selectedCube);
      }
    }
  }

  // 如果在拖动过程中，更新立方体属性信息
  if (isDragging && selectedCube) {
    updateCubeProperties();
  }
};

// 添加检查并吸附到其他立方体的函数
const checkAndSnapToCubes = () => {
  if (!selectedCube) return;

  // 重置所有立方体的材质颜色
  resetAllCubesColor();

  // 获取当前选中立方体的尺寸和位置
  const selectedGeometry = selectedCube.geometry as THREE.BoxGeometry;
  const selectedSize = new THREE.Vector3();
  if (selectedGeometry.boundingBox === null) {
    selectedGeometry.computeBoundingBox();
  }
  selectedGeometry.boundingBox?.getSize(selectedSize);

  // 获取选中立方体的半尺寸
  const selectedHalfSize = selectedSize.clone().multiplyScalar(0.5);

  // 获取选中立方体的世界位置
  const selectedPosition = new THREE.Vector3();
  (selectedCube as any).getWorldPosition(selectedPosition);

  // 存储所有可能的吸附信息
  const snapCandidates: any[] = [];

  // 计算选中立方体的8个角点位置
  const selectedCorners = [
    new THREE.Vector3(selectedPosition.x - selectedHalfSize.x, selectedPosition.y - selectedHalfSize.y, selectedPosition.z - selectedHalfSize.z),
    new THREE.Vector3(selectedPosition.x + selectedHalfSize.x, selectedPosition.y - selectedHalfSize.y, selectedPosition.z - selectedHalfSize.z),
    new THREE.Vector3(selectedPosition.x - selectedHalfSize.x, selectedPosition.y + selectedHalfSize.y, selectedPosition.z - selectedHalfSize.z),
    new THREE.Vector3(selectedPosition.x + selectedHalfSize.x, selectedPosition.y + selectedHalfSize.y, selectedPosition.z - selectedHalfSize.z),
    new THREE.Vector3(selectedPosition.x - selectedHalfSize.x, selectedPosition.y - selectedHalfSize.y, selectedPosition.z + selectedHalfSize.z),
    new THREE.Vector3(selectedPosition.x + selectedHalfSize.x, selectedPosition.y - selectedHalfSize.y, selectedPosition.z + selectedHalfSize.z),
    new THREE.Vector3(selectedPosition.x - selectedHalfSize.x, selectedPosition.y + selectedHalfSize.y, selectedPosition.z + selectedHalfSize.z),
    new THREE.Vector3(selectedPosition.x + selectedHalfSize.x, selectedPosition.y + selectedHalfSize.y, selectedPosition.z + selectedHalfSize.z)
  ];

  // 遍历场景中的所有立方体
  scene.children.forEach(child => {
    // 跳过非立方体对象和选中的立方体
    if (!(child instanceof THREE.Mesh) ||
        !(child.geometry instanceof THREE.BoxGeometry) ||
        child === selectedCube) {
      return;
    }

    // 获取目标立方体的尺寸和位置
    const targetGeometry = child.geometry as THREE.BoxGeometry;
    const targetSize = new THREE.Vector3();
    if (targetGeometry.boundingBox === null) {
      targetGeometry.computeBoundingBox();
    }
    targetGeometry.boundingBox?.getSize(targetSize);

    // 获取目标立方体的半尺寸
    const targetHalfSize = targetSize.clone().multiplyScalar(0.5);

    // 获取目标立方体的世界位置
    const targetPosition = new THREE.Vector3();
    (child as any).getWorldPosition(targetPosition);

    // 计算目标立方体的8个角点位置
    const targetCorners = [
      new THREE.Vector3(targetPosition.x - targetHalfSize.x, targetPosition.y - targetHalfSize.y, targetPosition.z - targetHalfSize.z),
      new THREE.Vector3(targetPosition.x + targetHalfSize.x, targetPosition.y - targetHalfSize.y, targetPosition.z - targetHalfSize.z),
      new THREE.Vector3(targetPosition.x - targetHalfSize.x, targetPosition.y + targetHalfSize.y, targetPosition.z - targetHalfSize.z),
      new THREE.Vector3(targetPosition.x + targetHalfSize.x, targetPosition.y + targetHalfSize.y, targetPosition.z - targetHalfSize.z),
      new THREE.Vector3(targetPosition.x - targetHalfSize.x, targetPosition.y - targetHalfSize.y, targetPosition.z + targetHalfSize.z),
      new THREE.Vector3(targetPosition.x + targetHalfSize.x, targetPosition.y - targetHalfSize.y, targetPosition.z + targetHalfSize.z),
      new THREE.Vector3(targetPosition.x - targetHalfSize.x, targetPosition.y + targetHalfSize.y, targetPosition.z + targetHalfSize.z),
      new THREE.Vector3(targetPosition.x + targetHalfSize.x, targetPosition.y + targetHalfSize.y, targetPosition.z + targetHalfSize.z)
    ];

    // 检查角点吸附
    for (let i = 0; i < selectedCorners.length; i++) {
      for (let j = 0; j < targetCorners.length; j++) {
        const distance = (selectedCorners[i] as any).distanceTo(targetCorners[j]);
        if (distance < CORNER_SNAP_THRESHOLD) {
          // 计算需要移动的向量，使选中立方体的角点与目标立方体的角点对齐
          const moveVector = new THREE.Vector3();
          (moveVector as any).subVectors(targetCorners[j], selectedCorners[i]);
          const newPosition = new THREE.Vector3();
          (newPosition as any).addVectors(selectedPosition, moveVector);

          snapCandidates.push({
            axis: 'corner',
            distance: distance,
            targetCube: child,
            snapPosition: newPosition,
            cornerIndex: [i, j] // 记录角点索引，用于调试
          });
        }
      }
    }

    // 计算动态曼哈顿距离阈值
    // 长的和的一半 + 宽的和的一半 + 微小偏移
    const dynamicThreshold =
      (selectedSize.x + targetSize.x) / 2 +
      (selectedSize.z + targetSize.z) / 2 +
      SNAP_OFFSET;

    // 计算两个立方体中心点之间的曼哈顿距离
    const manhattanDistance =
      Math.abs(selectedPosition.x - targetPosition.x) +
      Math.abs(selectedPosition.y - targetPosition.y) +
      Math.abs(selectedPosition.z - targetPosition.z);

    // 如果曼哈顿距离大于动态阈值，跳过此立方体的面吸附检查
    if (manhattanDistance > dynamicThreshold) {
      return;
    }

    // 检查六个方向的吸附可能性
    // X轴正方向（选中立方体的右面与目标立方体的左面）
    const distanceXPos = targetPosition.x - targetHalfSize.x - (selectedPosition.x + selectedHalfSize.x);
    if (Math.abs(distanceXPos) < SNAP_THRESHOLD) {
      snapCandidates.push({
        axis: 'x',
        direction: 1,
        distance: Math.abs(distanceXPos),
        targetCube: child,
        snapPosition: new THREE.Vector3(
          targetPosition.x - targetHalfSize.x - selectedHalfSize.x,
          selectedPosition.y,
          selectedPosition.z
        )
      });
    }

    // X轴负方向（选中立方体的左面与目标立方体的右面）
    const distanceXNeg = selectedPosition.x - selectedHalfSize.x - (targetPosition.x + targetHalfSize.x);
    if (Math.abs(distanceXNeg) < SNAP_THRESHOLD) {
      snapCandidates.push({
        axis: 'x',
        direction: -1,
        distance: Math.abs(distanceXNeg),
        targetCube: child,
        snapPosition: new THREE.Vector3(
          targetPosition.x + targetHalfSize.x + selectedHalfSize.x,
          selectedPosition.y,
          selectedPosition.z
        )
      });
    }

    // Z轴正方向（选中立方体的前面与目标立方体的后面）
    const distanceZPos = targetPosition.z - targetHalfSize.z - (selectedPosition.z + selectedHalfSize.z);
    if (Math.abs(distanceZPos) < SNAP_THRESHOLD) {
      snapCandidates.push({
        axis: 'z',
        direction: 1,
        distance: Math.abs(distanceZPos),
        targetCube: child,
        snapPosition: new THREE.Vector3(
          selectedPosition.x,
          selectedPosition.y,
          targetPosition.z - targetHalfSize.z - selectedHalfSize.z
        )
      });
    }

    // Z轴负方向（选中立方体的后面与目标立方体的前面）
    const distanceZNeg = selectedPosition.z - selectedHalfSize.z - (targetPosition.z + targetHalfSize.z);
    if (Math.abs(distanceZNeg) < SNAP_THRESHOLD) {
      snapCandidates.push({
        axis: 'z',
        direction: -1,
        distance: Math.abs(distanceZNeg),
        targetCube: child,
        snapPosition: new THREE.Vector3(
          selectedPosition.x,
          selectedPosition.y,
          targetPosition.z + targetHalfSize.z + selectedHalfSize.z
        )
      });
    }

    // Y轴正方向（选中立方体的上面与目标立方体的下面）
    const distanceYPos = targetPosition.y - targetHalfSize.y - (selectedPosition.y + selectedHalfSize.y);
    if (Math.abs(distanceYPos) < SNAP_THRESHOLD) {
      snapCandidates.push({
        axis: 'y',
        direction: 1,
        distance: Math.abs(distanceYPos),
        targetCube: child,
        snapPosition: new THREE.Vector3(
          selectedPosition.x,
          targetPosition.y - targetHalfSize.y - selectedHalfSize.y,
          selectedPosition.z
        )
      });
    }

    // Y轴负方向（选中立方体的下面与目标立方体的上面）
    const distanceYNeg = selectedPosition.y - selectedHalfSize.y - (targetPosition.y + targetHalfSize.y);
    if (Math.abs(distanceYNeg) < SNAP_THRESHOLD) {
      snapCandidates.push({
        axis: 'y',
        direction: -1,
        distance: Math.abs(distanceYNeg),
        targetCube: child,
        snapPosition: new THREE.Vector3(
          selectedPosition.x,
          targetPosition.y + targetHalfSize.y + selectedHalfSize.y,
          selectedPosition.z
        )
      });
    }
  });

  // 如果没有找到任何吸附候选，直接返回
  if (snapCandidates.length === 0) {
    return;
  }

  // 检查是否有角点吸附候选
  const cornerCandidates = snapCandidates.filter(c => c.axis === 'corner');
  if (cornerCandidates.length > 0) {
    // 找到距离最小的角点吸附候选
    const bestCornerCandidate = cornerCandidates.reduce((prev, current) =>
      prev.distance < current.distance ? prev : current
    );

    // 应用角点吸附
    selectedCube.position.copy(bestCornerCandidate.snapPosition);

    // 高亮显示目标立方体
    const targetMaterial = (bestCornerCandidate.targetCube as THREE.Mesh).material as THREE.MeshStandardMaterial;
    (targetMaterial as any).emissive.set(SNAP_HIGHLIGHT_COLOR);
    (targetMaterial as any).emissiveIntensity = 0.5;

    return; // 如果有角点吸附，优先使用角点吸附，不再考虑面吸附
  }

  // 按轴向对吸附候选进行分组
  const xAxisCandidates = snapCandidates.filter(c => c.axis === 'x');
  const yAxisCandidates = snapCandidates.filter(c => c.axis === 'y');
  const zAxisCandidates = snapCandidates.filter(c => c.axis === 'z');

  // 从每个轴向选择距离最小的候选
  const bestCandidates = [];

  if (xAxisCandidates.length > 0) {
    bestCandidates.push(xAxisCandidates.reduce((prev, current) =>
      prev.distance < current.distance ? prev : current
    ));
  }

  if (yAxisCandidates.length > 0) {
    bestCandidates.push(yAxisCandidates.reduce((prev, current) =>
      prev.distance < current.distance ? prev : current
    ));
  }

  if (zAxisCandidates.length > 0) {
    bestCandidates.push(zAxisCandidates.reduce((prev, current) =>
      prev.distance < current.distance ? prev : current
    ));
  }

  // 如果有多个最佳候选，应用多轴吸附
  if (bestCandidates.length > 0) {
    // 创建一个新的位置向量，初始为当前位置
    const newPosition = selectedCube.position.clone();

    // 应用每个轴向的吸附
    bestCandidates.forEach(candidate => {
      // 根据轴向更新对应的坐标
      if (candidate.axis === 'x') {
        newPosition.x = (candidate.snapPosition as THREE.Vector3).x;
      } else if (candidate.axis === 'y') {
        newPosition.y = (candidate.snapPosition as THREE.Vector3).y;
      } else if (candidate.axis === 'z') {
        newPosition.z = (candidate.snapPosition as THREE.Vector3).z;
      }

      // 高亮显示目标立方体
      const targetMaterial = (candidate.targetCube as THREE.Mesh).material as THREE.MeshStandardMaterial;
      (targetMaterial as any).emissive.set(SNAP_HIGHLIGHT_COLOR);
      (targetMaterial as any).emissiveIntensity = 0.5;
    });

    // 更新立方体位置
    selectedCube.position.copy(newPosition);
  }
};

// 重置所有立方体的颜色
const resetAllCubesColor = () => {
  scene.children.forEach(child => {
    if (child instanceof THREE.Mesh &&
        child.geometry instanceof THREE.BoxGeometry) {
      const material = child.material as THREE.MeshStandardMaterial;
      (material as any).emissive.set(0x000000);
      (material as any).emissiveIntensity = 0;
    }
  });
};

// 处理鼠标释放事件
const onMouseUp = () => {
  // 如果没有在拖动，直接返回
  if (!isDragging) return;

  // 结束拖动
  isDragging = false;

  // 移除拖动线段
  removeDragLine();

  // 重新启用轨道控制器
  orbitControls.enabled = true;

  // 重置所有立方体的颜色
  resetAllCubesColor();

  // 保存控制点的最终位置为新的原始位置
  if (selectedControlPoint) {
    controlPointOriginalPosition = selectedControlPoint.position.clone();
  }

  // 更新立方体的原始位置和尺寸
  if (selectedCube) {
    // 更新立方体的原始位置 - 确保保存当前完整的位置
    selectedCube.userData.originalPosition = selectedCube.position.clone();

    // 更新立方体的几何体以匹配当前的缩放
    if ((selectedCube as any).scale.x !== 1 || (selectedCube as any).scale.y !== 1 || (selectedCube as any).scale.z !== 1) {
      // 获取当前几何体的尺寸
      const geometry = selectedCube.geometry as THREE.BoxGeometry;
      const size = new THREE.Vector3();
      if (geometry.boundingBox === null) {
        geometry.computeBoundingBox();
      }
      geometry.boundingBox?.getSize(size);

      // 计算新的尺寸
      const newWidth = size.x * (selectedCube as any).scale.x;
      const newHeight = size.y * (selectedCube as any).scale.y;
      const newDepth = size.z * (selectedCube as any).scale.z;

      // 创建新的几何体
      const newGeometry = new THREE.BoxGeometry(newWidth, newHeight, newDepth);

      // 替换几何体
      (selectedCube.geometry as any).dispose(); // 释放旧几何体
      selectedCube.geometry = newGeometry;

      // 重置缩放
      (selectedCube as any).scale.set(1, 1, 1);

      // 更新边框
      // 移除旧边框
      const edgesToRemove: THREE.Object3D[] = [];
      selectedCube.children.forEach(child => {
        if (child instanceof THREE.LineSegments) {
          edgesToRemove.push(child);
        }
      });
      edgesToRemove.forEach(edge => {
        selectedCube?.remove(edge);
      });

      // 添加新边框
      const edges = new THREE.LineSegments(
        new THREE.EdgesGeometry(newGeometry),
        new THREE.LineBasicMaterial({ color: 0x000000 })
      );
      selectedCube.add(edges);

      // 更新原始尺寸
      selectedCube.userData.originalScale = new THREE.Vector3(newWidth, newHeight, newDepth);
    }

    // 更新控制点位置
    updateAllControlPointsPositions(selectedCube);
  }

  // 如果有选中的立方体，更新属性信息
  if (selectedCube) {
    updateCubeProperties();
  }
};

// 添加一个新函数来更新所有控制点位置
const updateAllControlPointsPositions = (cube: THREE.Mesh) => {
  // 获取立方体的尺寸
  const geometry = cube.geometry as THREE.BoxGeometry;
  const size = new THREE.Vector3();
  if (geometry.boundingBox === null) {
    geometry.computeBoundingBox();
  }
  geometry.boundingBox?.getSize(size);

  // 控制点的位置（相对于立方体中心）
  const halfSize = size.clone().multiplyScalar(0.5);

  // 更新所有控制点的位置
  cube.children.forEach(child => {
    if (child instanceof THREE.Mesh &&
        child.geometry instanceof THREE.SphereGeometry &&
        child.userData.isControlPoint) {

      // 获取控制点的法向量
      const normal = child.userData.normal as THREE.Vector3;

      // 根据法向量确定控制点的位置
      if (normal.y === 1) { // 上
        child.position.set(0, halfSize.y, 0);
      } else if (normal.x === 1) { // 右
        child.position.set(halfSize.x, 0, 0);
      } else if (normal.z === 1) { // 前
        child.position.set(0, 0, halfSize.z);
      } else if (normal.x === -1) { // 左
        child.position.set(-halfSize.x, 0, 0);
      } else if (normal.z === -1) { // 后
        child.position.set(0, 0, -halfSize.z);
      } else if (normal.y === -1) { // 底部（用于平移）- 确保始终在底面中心
        child.position.set(0, -halfSize.y, 0);
      }

      // 如果这是当前选中的控制点，更新原始位置
      if (child === selectedControlPoint) {
        controlPointOriginalPosition = child.position.clone();
      }
    }
  });
};

// 初始化场景
const initScene = () => {
  if (!canvasRef.value) return;

  // 创建场景
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xf0f0f0);

  // 创建相机 - 使用正交相机实现真正的等轴侧视图
  const aspect = window.innerWidth / window.innerHeight;
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
  // 等轴侧视图的相机位置通常是三个轴上的值相等
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
  const container = document.querySelector('.viewport-container') as HTMLElement;
  if (container) {
    const width = container.clientWidth;
    const height = container.clientHeight;
    renderer.setSize(width, height);
  } else {
    renderer.setSize(window.innerWidth, window.innerHeight);
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

  // 初始化射线和鼠标位置
  raycaster = new THREE.Raycaster();
  // 设置射线检测的精度
  raycaster.params.Line.threshold = 0.01;
  raycaster.params.Points.threshold = 0.01;
  raycaster.params.Mesh.threshold = 0;

  mouse = new THREE.Vector2();

  // 添加鼠标事件监听
  canvasRef.value.addEventListener('mousedown', onMouseDown);
  canvasRef.value.addEventListener('mousemove', onMouseMove);
  canvasRef.value.addEventListener('mouseup', onMouseUp);

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
  }
};

// 动画循环
const animate = () => {
  requestAnimationFrame(animate);

  // 如果有选中的立方体，确保所有控制点保持固定大小
  if (selectedCube) {
    // 获取立方体的世界缩放
    const worldScale = new THREE.Vector3();
    (selectedCube as any).getWorldScale(worldScale);

    // 计算反向缩放值
    const inverseScale = new THREE.Vector3(
      worldScale.x !== 0 ? 1 / worldScale.x : 1,
      worldScale.y !== 0 ? 1 / worldScale.y : 1,
      worldScale.z !== 0 ? 1 / worldScale.z : 1
    );

    // 应用反向缩放到所有控制点
    selectedCube.children.forEach(child => {
      if (child instanceof THREE.Mesh &&
          child.geometry instanceof THREE.SphereGeometry &&
          child.userData.isControlPoint) {
        (child as any).scale.copy(inverseScale);
      }
    });
  }

  orbitControls.update();

  renderer.render(scene, camera);
};

// 组件挂载时初始化
onMounted(() => {
  console.log('组件已挂载，初始化场景');
  initScene();

  // 添加窗口大小调整监听
  window.addEventListener('resize', onWindowResize);

  // 确保初始化后立即调整大小
  setTimeout(() => {
    onWindowResize();
  }, 100);

  // 检查URL参数，确定是否是从第二页返回的
  const urlParams = new URLSearchParams(window.location.search);
  const returnFromSecond = urlParams.get('returnFromSecond');

  // 如果有保存的模型数据且是从第二页返回，则加载模型
  const savedModelData = localStorage.getItem('modelData');
  if (savedModelData && returnFromSecond === 'true') {
    try {
      const modelData = JSON.parse(savedModelData);
      loadSavedCubes(modelData.cubes);
      console.log('已成功加载保存的立方体模型');
    } catch (error) {
      console.error('加载保存的模型失败:', error);
    }
  }
});

// 组件卸载前清理
onBeforeUnmount(() => {
  console.log('组件卸载，清理资源');
  window.removeEventListener('resize', onWindowResize);

  // 移除鼠标事件监听
  if (canvasRef.value) {
    canvasRef.value.removeEventListener('mousedown', onMouseDown);
    canvasRef.value.removeEventListener('mousemove', onMouseMove);
    canvasRef.value.removeEventListener('mouseup', onMouseUp);
  }

  // 释放资源
  if (renderer) {
    renderer.dispose();
  }
});

// 检查立方体模型并完成建模
const checkAndCompleteCubeModeling = () => {
  // 获取场景中所有立方体
  const cubesData = extractCubesData(scene);

  // 如果没有立方体，显示提示
  if (cubesData.length === 0) {
    alert('场景中没有任何立方体，请先创建立方体！');
    return;
  }

  // 转换为三维区间
  const intervals = cubesToIntervals(cubesData);

  // 存储存在问题的立方体对
  let problematicPairs = [];

  // 首先检查是否存在相交的立方体对
  for (let i = 0; i < intervals.length; i++) {
    for (let j = i + 1; j < intervals.length; j++) {
      // 检查是否相交（有重叠）
      if (intervalsIntersect(intervals[i], intervals[j])) {
        problematicPairs.push({
          type: '相交',
          cube1: i + 1,
          cube2: j + 1,
          position1: cubesData[i].position,
          position2: cubesData[j].position
        });
      }
    }
  }

  // 如果存在相交问题，直接显示错误
  if (problematicPairs.length > 0) {
    let errorMessage = '发现以下问题:\n\n';

    // 列出所有相交问题
    errorMessage += '【相交立方体】:\n';
    problematicPairs.forEach(pair => {
      errorMessage += `立方体 ${pair.cube1} 和立方体 ${pair.cube2} 相交\n`;
      errorMessage += `位置1: (${pair.position1.x.toFixed(2)}, ${pair.position1.y.toFixed(2)}, ${pair.position1.z.toFixed(2)})\n`;
      errorMessage += `位置2: (${pair.position2.x.toFixed(2)}, ${pair.position2.y.toFixed(2)}, ${pair.position2.z.toFixed(2)})\n\n`;
    });

    errorMessage += '请修正这些问题后再完成建模。';

    // 显示报错弹窗
    alert(errorMessage);
    return;
  }

  // 在没有相交问题的情况下，检查连通性
  // 使用连通性算法检查所有立方体是否形成一个整体
  const isConnected = areAllCubesConnected(intervals);

  if (!isConnected) {
    // 找出所有不连通的组
    const disconnectedGroups = findDisconnectedGroups(intervals);

    let errorMessage = '模型存在不连通的部分:\n\n';
    errorMessage += '以下立方体组之间没有面接触连接，形成了分离的部分:\n\n';

    // 显示每个连通分量
    disconnectedGroups.forEach((group, index) => {
      errorMessage += `组 ${index + 1}: 包含立方体 ${group.map(i => i + 1).join(', ')}\n`;

      // 显示该组的第一个立方体的位置作为参考
      const firstCube = group[0];
      errorMessage += `参考位置: (${cubesData[firstCube].position.x.toFixed(2)}, ${cubesData[firstCube].position.y.toFixed(2)}, ${cubesData[firstCube].position.z.toFixed(2)})\n\n`;
    });

    errorMessage += '请确保所有立方体通过面相贴连接成一个整体。';

    // 显示报错弹窗
    alert(errorMessage);
    return;
  }

  // 所有检查都通过，显示成功消息并在用户确认后跳转
  // 使用window.confirm以确保用户点击确定后才跳转
  if (window.confirm('恭喜！所有立方体模型均符合要求，形成了一个连通的整体。')) {
    // 保存当前场景数据到localStorage（可选）
    const sceneData = {
      cubes: cubesData
    };
    localStorage.setItem('modelData', JSON.stringify(sceneData));

    // 导航到第二个页面
    router.push('/second');
  }
};

// 加载保存的立方体
const loadSavedCubes = (cubesData: any[]) => {
  if (!Array.isArray(cubesData) || cubesData.length === 0) return;

  // 清除现有立方体
  const cubesToRemove: THREE.Object3D[] = [];
  scene.children.forEach(child => {
    if (child instanceof THREE.Mesh && child.geometry instanceof THREE.BoxGeometry) {
      cubesToRemove.push(child);
    }
  });
  cubesToRemove.forEach(cube => scene.remove(cube));

  // 创建新立方体
  cubesData.forEach(cubeData => {
    // 创建几何体
    const geometry = new THREE.BoxGeometry(
      cubeData.size.width,
      cubeData.size.height,
      cubeData.size.depth
    );

    // 创建材质
    const material = new THREE.MeshStandardMaterial({
      color: 0x00aaff,
      transparent: true,
      opacity: 0.7
    });

    // 创建网格
    const cube = new THREE.Mesh(geometry, material);

    // 设置位置
    cube.position.set(
      cubeData.position.x,
      cubeData.position.y,
      cubeData.position.z
    );

    // 添加边框
    const edges = new THREE.LineSegments(
      new THREE.EdgesGeometry(geometry),
      new THREE.LineBasicMaterial({ color: 0x000000 })
    );
    cube.add(edges);

    // 添加原始缩放数据
    cube.userData.originalScale = new THREE.Vector3(
      cubeData.size.width,
      cubeData.size.height,
      cubeData.size.depth
    );

    // 添加到场景
    scene.add(cube);
  });

  // 清除选中状态
  selectedCube = null;
  selectedControlPoint = null;
  showSidebar.value = false;
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
}

.viewport-container {
  width: 95%;
  height: 92%;
  bottom: 10px;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  position: relative;
}

.canvas {
  width: 100%;
  height: 100%;
  display: block;
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

.create-button {
  padding: 8px 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s;
}

.create-button:hover {
  background-color: #45a049;
}

/* 教程面板样式 */
.tutorial-panel {
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  width: 100%;
}

.tutorial-header {
  background-color: #333;
  color: white;
  padding: 8px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}

.header-text {
  font-size: 12px;
}

.toggle-button {
  background-color: transparent;
  border: 1px solid white;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.toggle-button:hover {
  background-color: rgba(255, 255, 255, 0.2);
}

.tutorial-content {
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
}

.tutorial-item {
  display: flex;
  margin-bottom: 8px;
  align-items: flex-start;
}

.tutorial-icon {
  font-size: 9px;
  margin-right: 4px;
  min-width: 24px;
  text-align: center;
}

.tutorial-text {
  font-size: 10px;
  line-height: 1.4;
}

/* 刘海屏标签样式 */
.notch-container {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .viewport-container {
    width: 95%;
    height: 95%;
  }

  .create-button {
    padding: 6px 10px;
    font-size: 10px;
  }

  .tutorial-panel {
    max-width: 250px;
  }

  .tutorial-header {
    padding: 6px 10px;
    font-size: 10px;
  }

  .header-text {
    font-size: 10px;
  }

  .toggle-button {
    font-size: 10px;
  }

  .tutorial-icon {
    font-size: 16px;
  }

  .tutorial-text {
    font-size: 10px;
  }

  .notch {
    padding: 3px 8px 4px 8px;
  }

  .notch-text {
    font-size: 6px;
  }

  .sidebar {
    width: 150px;
  }

  .property-row {
    font-size: 9px;
  }

  .delete-button {
    font-size: 10px;
    padding: 6px 8px;
  }

  .delete-icon {
    font-size: 12px;
  }

  .complete-button {
    padding: 8px 16px;
    font-size: 12px;
  }

  .complete-icon {
    font-size: 14px;
    margin-right: 4px;
  }

}

/* 侧边栏样式 */
.sidebar {
  position: absolute;
  top: 15px;
  right: -250px;
  width: 200px;
  background-color: rgba(255, 255, 255, 0.9);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  overflow: hidden;
  transition: right 0.3s ease-in-out;
  z-index: 10;
}

.sidebar-visible {
  right: 15px;
}

.sidebar-header {
  background-color: #333;
  color: white;
  padding: 8px 14px;
  font-weight: bold;
}

.sidebar-content {
  padding: 10px;
}

.property-group {
  margin-bottom: 15px;
}

.property-title {
  font-size: 12px;
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
  border-bottom: 1px solid #ddd;
  padding-bottom: 3px;
}

.property-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 11px;
}

.property-label {
  color: #666;
  flex: 1;
}

.property-value {
  font-weight: bold;
  color: #333;
  flex: 1;
  text-align: right;
}

.property-input {
  flex: 1;
  text-align: right;
}

.size-input {
  width: 50px;
  padding: 2px 4px;
  border: 1px solid #ccc;
  border-radius: 3px;
  font-size: 11px;
  text-align: right;
  background-color: rgba(255, 255, 255, 0.8);
}

.size-input:focus {
  outline: none;
  border-color: #4CAF50;
  box-shadow: 0 0 3px rgba(76, 175, 80, 0.5);
}

/* 删除按钮样式 */
.delete-button-container {
  margin-top: 20px;
  display: flex;
  justify-content: center;
}

.delete-button {
  background-color: #ff3b30;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 12px;
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  transition: background-color 0.3s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.delete-button:hover {
  background-color: #d9302c;
}

.delete-icon {
  margin-right: 5px;
  font-size: 14px;
}

/* 完成按钮样式 */
.complete-button-container {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.complete-button {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.complete-button:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
}

.complete-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.complete-icon {
  margin-right: 6px;
  font-size: 18px;
}

/* 语言切换按钮样式 */
.language-switch {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 10;
}

.language-and-video-button {
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
  z-index: 99999;
}

.language-button:hover {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}


</style>
