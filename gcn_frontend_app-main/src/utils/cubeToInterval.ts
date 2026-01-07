// @ts-ignore
import * as THREE from 'three';

export interface CubeData {
  position: {
    x: number;
    y: number;
    z: number;
  };
  size: {
    width: number;
    height: number;
    depth: number;
  };
}

export interface Interval3D {
  min: {
    x: number;
    y: number;
    z: number;
  };
  max: {
    x: number;
    y: number;
    z: number;
  };
}

/**
 * 将立方体数据转换为三维区间形式
 * 输入：立方体数据对象，包含位置和尺寸信息
 * 输出：三维区间对象，包含最小点和最大点坐标
 */
export function cubeToInterval(cubeData: CubeData): Interval3D {
  // 检查输入数据是否有效
  if (!cubeData || !cubeData.position || !cubeData.size) {
    throw new Error('无效的立方体数据：必须包含位置和尺寸信息');
  }
  
  const { position, size } = cubeData;
  
  // 计算半尺寸
  const halfWidth = size.width / 2;
  const halfHeight = size.height / 2;
  const halfDepth = size.depth / 2;
  
  // 计算最小点和最大点
  let min = {
    x: position.x - halfWidth,
    y: position.y - halfHeight,
    z: position.z - halfDepth
  };
  
  let max = {
    x: position.x + halfWidth,
    y: position.y + halfHeight,
    z: position.z + halfDepth
  };
  
  // 将所有坐标值四舍五入到0.01精度（保留两位小数）
  min = {
    x: Math.round(min.x * 100) / 100,
    y: Math.round(min.y * 100) / 100,
    z: Math.round(min.z * 100) / 100
  };
  
  max = {
    x: Math.round(max.x * 100) / 100,
    y: Math.round(max.y * 100) / 100,
    z: Math.round(max.z * 100) / 100
  };
  
  return { min, max };
}

/**
 * 将多个立方体数据转换为三维区间形式
 */
export function cubesToIntervals(cubesData: CubeData[]): Interval3D[] {
  if (!Array.isArray(cubesData)) {
    throw new Error('输入必须是立方体数据数组');
  }
  
  return cubesData.map(cubeData => cubeToInterval(cubeData));
}

/**
 * 检查两个三维区间是否相交
 */
export function intervalsIntersect(interval1: Interval3D, interval2: Interval3D): boolean {
  // 检查X轴是否有重叠
  const overlapX = interval1.max.x > interval2.min.x && interval1.min.x < interval2.max.x;
  // 检查Y轴是否有重叠
  const overlapY = interval1.max.y > interval2.min.y && interval1.min.y < interval2.max.y;
  // 检查Z轴是否有重叠
  const overlapZ = interval1.max.z > interval2.min.z && interval1.min.z < interval2.max.z;
  
  // 如果三个轴都有重叠，则区间相交
  return overlapX && overlapY && overlapZ;
}

/**
 * 检查两个三维区间是否有面接触
 * 面接触指在一个维度上边界相等，而在其他两个维度上有重叠
 */
export function intervalsFaceTouch(interval1: Interval3D, interval2: Interval3D): boolean {
  // 检查每个轴上是否有边界接触
  const touchX = interval1.max.x === interval2.min.x || interval1.min.x === interval2.max.x;
  const touchY = interval1.max.y === interval2.min.y || interval1.min.y === interval2.max.y;
  const touchZ = interval1.max.z === interval2.min.z || interval1.min.z === interval2.max.z;
  
  // 检查每个轴上是否有重叠（不包括边界）
  // 注意：这里使用 >= 和 <= 是为了包含边界情况
  const overlapX = interval1.max.x >= interval2.min.x && interval1.min.x <= interval2.max.x;
  const overlapY = interval1.max.y >= interval2.min.y && interval1.min.y <= interval2.max.y;
  const overlapZ = interval1.max.z >= interval2.min.z && interval1.min.z <= interval2.max.z;
  
  // 面接触情况：一个维度上有边界接触，其他两个维度上有重叠
  const faceX = touchX && overlapY && overlapZ;
  const faceY = touchY && overlapX && overlapZ;
  const faceZ = touchZ && overlapX && overlapY;
  
  return faceX || faceY || faceZ;
}

/**
 * 检查两个三维区间是否完全分离
 */
export function intervalsAreDisjoint(interval1: Interval3D, interval2: Interval3D): boolean {
  // 检查是否在任意一个轴上完全分离
  // 如果一个区间的最小值大于另一个区间的最大值，或者一个区间的最大值小于另一个区间的最小值，则在该轴上完全分离
  const disjointX = interval1.max.x < interval2.min.x || interval1.min.x > interval2.max.x;
  const disjointY = interval1.max.y < interval2.min.y || interval1.min.y > interval2.max.y;
  const disjointZ = interval1.max.z < interval2.min.z || interval1.min.z > interval2.max.z;
  
  // 检测是否只有线接触（边接触）
  // 边接触意味着在两个维度上的值恰好相等（边界点相等），而在第三个维度上有重叠
  const touchX = interval1.max.x === interval2.min.x || interval1.min.x === interval2.max.x;
  const touchY = interval1.max.y === interval2.min.y || interval1.min.y === interval2.max.y;
  const touchZ = interval1.max.z === interval2.min.z || interval1.min.z === interval2.max.z;
  
  // 计算接触的维度数量
  const touchCount = (touchX ? 1 : 0) + (touchY ? 1 : 0) + (touchZ ? 1 : 0);
  
  // 边接触：至少两个维度上的边界相等，第三个维度有重叠
  const isEdgeTouch = touchCount >= 2;
  
  // 只要有一个轴上完全分离，或者只是边接触，就认为是分离的
  return disjointX || disjointY || disjointZ || isEdgeTouch;
}

/**
 * 检查一组立方体是否形成连通整体
 * 使用深度优先搜索算法检查连通性
 * 
 * @param intervals 立方体的三维区间数组
 * @returns 如果所有立方体形成一个连通整体，返回true；否则返回false
 */
export function areAllCubesConnected(intervals: Interval3D[]): boolean {
  if (intervals.length <= 1) {
    return true; // 0个或1个立方体始终被认为是连通的
  }
  
  // 创建邻接表表示立方体之间的连接关系
  const adjacencyList: number[][] = Array(intervals.length).fill(0).map(() => []);
  
  // 构建邻接表
  for (let i = 0; i < intervals.length; i++) {
    for (let j = i + 1; j < intervals.length; j++) {
      // 如果两个立方体面接触，则添加边
      if (intervalsFaceTouch(intervals[i], intervals[j])) {
        adjacencyList[i].push(j);
        adjacencyList[j].push(i);
      }
    }
  }
  
  // 使用DFS检查图的连通性
  const visited = new Array(intervals.length).fill(false);
  
  // DFS函数
  function dfs(node: number) {
    visited[node] = true;
    for (const neighbor of adjacencyList[node]) {
      if (!visited[neighbor]) {
        dfs(neighbor);
      }
    }
  }
  
  // 从第一个节点开始DFS
  dfs(0);
  
  // 检查是否所有节点都被访问到
  return visited.every(v => v);
}

/**
 * 检查所有立方体是否存在孤立的部分（不连通）
 * 
 * @param intervals 立方体的三维区间数组
 * @returns 孤立部分的索引组，每个子数组表示一个连通分量
 */
export function findDisconnectedGroups(intervals: Interval3D[]): number[][] {
  if (intervals.length <= 1) {
    return intervals.length === 0 ? [] : [[0]]; // 返回空数组或包含单个元素的数组
  }
  
  // 创建邻接表表示立方体之间的连接关系
  const adjacencyList: number[][] = Array(intervals.length).fill(0).map(() => []);
  
  // 构建邻接表
  for (let i = 0; i < intervals.length; i++) {
    for (let j = i + 1; j < intervals.length; j++) {
      // 如果两个立方体面接触，则添加边
      if (intervalsFaceTouch(intervals[i], intervals[j])) {
        adjacencyList[i].push(j);
        adjacencyList[j].push(i);
      }
    }
  }
  
  // 用于记录访问状态
  const visited = new Array(intervals.length).fill(false);
  const groups: number[][] = [];
  
  // DFS函数，收集连通分量
  function dfs(node: number, component: number[]) {
    visited[node] = true;
    component.push(node);
    
    for (const neighbor of adjacencyList[node]) {
      if (!visited[neighbor]) {
        dfs(neighbor, component);
      }
    }
  }
  
  // 找出所有连通分量
  for (let i = 0; i < intervals.length; i++) {
    if (!visited[i]) {
      const component: number[] = [];
      dfs(i, component);
      groups.push(component);
    }
  }
  
  return groups;
}

/**
 * 从场景提取所有立方体数据
 */
export function extractCubesData(scene: any): CubeData[] {
  const cubesData: CubeData[] = [];
  
  scene.children.forEach((child: any) => {
    // 检查是否是立方体（Mesh 且几何体是 BoxGeometry）
    if (child instanceof THREE.Mesh && 
        child.geometry instanceof THREE.BoxGeometry) {
      
      // 获取尺寸
      const size = new THREE.Vector3();
      if (child.geometry.boundingBox === null) {
        child.geometry.computeBoundingBox();
      }
      // 使用非空断言，因为我们已经确保了boundingBox不为空
      child.geometry.boundingBox!.getSize(size);
      
      // 添加立方体数据
      cubesData.push({
        position: {
          x: child.position.x,
          y: child.position.y,
          z: child.position.z
        },
        size: {
          width: size.x,
          height: size.y,
          depth: size.z
        }
      });
    }
  });
  
  return cubesData;
}

/**
 * 将立方体拆分为6个面，每个面由有序顶点列表存储
 * @param cubeData 立方体数据
 * @returns 包含6个面的数组，每个面是一个有序顶点列表
 */
export interface Face {
  vertices: THREE.Vector3[];  // 顶点坐标数组
  normal: THREE.Vector3;      // 法向量
  color?: number;            // 颜色（可选）
  parentFaces?: number[];    // 所属的原始面索引（用于交集面）
  childIntersections?: number[]; // 属于该面的交集面索引（用于立方体面）
  parentFace?: number;       // 记录原始面的索引
}

export function cubesToFaces(cubesData: CubeData[]): Face[] {
  const allFaces: Face[] = [];
  
  cubesData.forEach((cubeData) => {
    const faces = cubeToFaces(cubeData);
    allFaces.push(...faces);
  });
  
  return allFaces;
}

export function cubeToFaces(cubeData: CubeData): Face[] {
  const { position, size } = cubeData;
  
  // 计算半尺寸
  const halfWidth = size.width / 2;
  const halfHeight = size.height / 2;
  const halfDepth = size.depth / 2;
  
  // 计算8个顶点的坐标
  const vertices = [
    new THREE.Vector3(position.x - halfWidth, position.y - halfHeight, position.z - halfDepth), // 0: 左下后
    new THREE.Vector3(position.x + halfWidth, position.y - halfHeight, position.z - halfDepth), // 1: 右下后
    new THREE.Vector3(position.x + halfWidth, position.y + halfHeight, position.z - halfDepth), // 2: 右上后
    new THREE.Vector3(position.x - halfWidth, position.y + halfHeight, position.z - halfDepth), // 3: 左上后
    new THREE.Vector3(position.x - halfWidth, position.y - halfHeight, position.z + halfDepth), // 4: 左下前
    new THREE.Vector3(position.x + halfWidth, position.y - halfHeight, position.z + halfDepth), // 5: 右下前
    new THREE.Vector3(position.x + halfWidth, position.y + halfHeight, position.z + halfDepth), // 6: 右上前
    new THREE.Vector3(position.x - halfWidth, position.y + halfHeight, position.z + halfDepth)  // 7: 左上前
  ];
  
  // 定义6个面，每个面由4个顶点索引组成，按照右手法则定义顶点顺序（顺时针）
  const faceIndices = [
    [0, 1, 2, 3], // 后面 (-Z)
    [4, 7, 6, 5], // 前面 (+Z)
    [0, 4, 5, 1], // 下面 (-Y)
    [3, 2, 6, 7], // 上面 (+Y)
    [0, 3, 7, 4], // 左面 (-X)
    [1, 5, 6, 2]  // 右面 (+X)
  ];
  
  // 定义面的法向量
  const normals = [
    new THREE.Vector3(0, 0, -1), // 后面
    new THREE.Vector3(0, 0, 1),  // 前面
    new THREE.Vector3(0, -1, 0), // 下面
    new THREE.Vector3(0, 1, 0),  // 上面
    new THREE.Vector3(-1, 0, 0), // 左面
    new THREE.Vector3(1, 0, 0)   // 右面
  ];
  
  // 为每个面分配不同的颜色（可选）
  const colors = [
    0x6666ff, // 后面 - 蓝色
    0x66ff66, // 前面 - 绿色
    0xff6666, // 下面 - 红色
    0xffff66, // 上面 - 黄色
    0xff66ff, // 左面 - 紫色
    0x66ffff  // 右面 - 青色
  ];
  
  // 创建面数组
  const faces: Face[] = [];
  
  for (let i = 0; i < 6; i++) {
    const faceVertices = faceIndices[i].map(index => vertices[index]);
    faces.push({
      vertices: faceVertices,
      normal: normals[i],
      color: colors[i]
    });
  }
  
  return faces;
}

/**
 * 在Three.js场景中渲染立方体的面
 * @param scene Three.js场景
 * @param faces 面数组
 * @param isIntersection 是否是交集面
 * @returns 渲染的面对象数组
 */
export function renderFacesInScene(scene: THREE.Scene, faces: Face[], isIntersection: boolean = false): THREE.Mesh[] {
  const meshes: THREE.Mesh[] = [];
  
  faces.forEach((face, index) => {
    // 创建几何体
    const geometry = new THREE.BufferGeometry();
    
    // 处理顶点
    let verticesArray: number[] = [];
    
    if (face.vertices.length === 4) {
      // 四边形 - 分解为两个三角形
      verticesArray = [
        // 第一个三角形
        face.vertices[0].x, face.vertices[0].y, face.vertices[0].z,
        face.vertices[1].x, face.vertices[1].y, face.vertices[1].z,
        face.vertices[2].x, face.vertices[2].y, face.vertices[2].z,
        // 第二个三角形
        face.vertices[0].x, face.vertices[0].y, face.vertices[0].z,
        face.vertices[2].x, face.vertices[2].y, face.vertices[2].z,
        face.vertices[3].x, face.vertices[3].y, face.vertices[3].z
      ];
    } else if (face.vertices.length > 4) {
      // 多于4个顶点的多边形，将其分解为多个三角形
      // 使用简单的三角形分解：(0,i,i+1)
      for (let i = 1; i < face.vertices.length - 1; i++) {
        verticesArray.push(
          face.vertices[0].x, face.vertices[0].y, face.vertices[0].z,
          face.vertices[i].x, face.vertices[i].y, face.vertices[i].z,
          face.vertices[i+1].x, face.vertices[i+1].y, face.vertices[i+1].z
        );
      }
    } else if (face.vertices.length === 3) {
      // 三角形 - 直接使用
      verticesArray = [
        face.vertices[0].x, face.vertices[0].y, face.vertices[0].z,
        face.vertices[1].x, face.vertices[1].y, face.vertices[1].z,
        face.vertices[2].x, face.vertices[2].y, face.vertices[2].z
      ];
    } else {
      // 少于3个顶点，无法形成面
      console.warn(`面 ${index} 顶点数量不足，无法渲染`);
      return;
    }
    
    // 设置顶点 - 使用类型断言解决类型错误
    (geometry as any).setAttribute(
      'position', 
      new (THREE as any).Float32BufferAttribute(verticesArray, 3)
    );
    
    // 计算法向量 - 使用类型断言解决类型错误
    (geometry as any).computeVertexNormals();
    
    // 创建材质
    const material = new THREE.MeshStandardMaterial({
      color: face.color || 0xffffff,
      transparent: true,
      opacity: isIntersection ? 0.9 : 0.8
    });
    
    // 设置双面可见 - 使用类型断言解决类型错误
    (material as any).side = (THREE as any).DoubleSide;
    
    // 创建网格
    const mesh = new THREE.Mesh(geometry, material);
    mesh.userData.isFace = true;
    mesh.userData.faceIndex = index;
    mesh.userData.isIntersection = isIntersection;
    
    // 保存面的法向量和顶点信息到userData
    mesh.userData.normal = face.normal;
    mesh.userData.vertices = face.vertices;
    
    // 如果是交集面，保存所属的原始面索引
    if (isIntersection && face.parentFaces) {
      mesh.userData.parentFaces = face.parentFaces;
    }
    
    // 如果是立方体面，保存属于它的交集面索引
    if (!isIntersection && face.childIntersections && face.childIntersections.length > 0) {
      mesh.userData.childIntersections = face.childIntersections;
    }
    
    // 如果是裁剪面，保存所属的原始面索引
    if (!isIntersection && face.parentFace !== undefined) {
      mesh.userData.parentFace = face.parentFace;
    }
    
    // 确保底面也能被选中
    // 检查是否是底面（法向量指向-Y方向）
    if (Math.abs(face.normal.y + 1) < 0.1) { // y ≈ -1
      // 为底面设置一个略微更高的渲染顺序，确保它能被射线检测到
      (mesh as any).renderOrder = 1;
    }
    
    // 添加到场景
    scene.add(mesh);
    
    // 添加到返回数组
    meshes.push(mesh);
  });
  
  return meshes;
}

/**
 * 检查两个面是否共面
 * @param face1 第一个面
 * @param face2 第二个面
 * @returns 如果两个面共面，返回true；否则返回false
 */
export function areFacesCoplanar(face1: Face, face2: Face): boolean {
  // 检查法向量是否平行（同向或反向）
  const dot = (face1.normal as any).dot(face2.normal);
  
  // 允许更大的误差范围，以捕获更多可能的共面情况
  const EPSILON = 0.01; // 增加误差容忍度
  const normalParallel = Math.abs(Math.abs(dot) - 1) < EPSILON;
  
  if (!normalParallel) {
    // console.log('法向量不平行:', Math.abs(Math.abs(dot) - 1));
    return false;
  }
  
  // 检查两个面是否在同一平面上
  // 取第一个面的一个点，计算它到第二个面的距离
  const point = face1.vertices[0];
  const plane = new (THREE as any).Plane().setFromNormalAndCoplanarPoint(face2.normal, face2.vertices[0]);
  const distance = Math.abs(plane.distanceToPoint(point));
  
  // 如果距离接近于0，则两个面在同一平面上
  const onSamePlane = distance < EPSILON;
  
  // 如果面共面，输出调试信息
  if (onSamePlane) {
    // console.log('面共面 - 法向量点积:', dot, '距离:', distance);
  }
  
  return onSamePlane;
}

/**
 * 检测两个面是否通过边连接（存在边和边共线）
 * @param face1 第一个面
 * @param face2 第二个面
 * @returns 如果两个面通过边连接，返回true；否则返回false
 */
export function areFacesConnectedByEdge(face1: Face, face2: Face): boolean {
  // 边的精度误差容忍度
  const EPSILON = 0.001;
  
  // 检查两个面的每一对边是否共线
  for (let i = 0; i < face1.vertices.length; i++) {
    const v1 = face1.vertices[i];
    const v2 = face1.vertices[(i + 1) % face1.vertices.length];
    
    for (let j = 0; j < face2.vertices.length; j++) {
      const v3 = face2.vertices[j];
      const v4 = face2.vertices[(j + 1) % face2.vertices.length];
      
      // 检查两条边是否共线
      if (areEdgesCollinear(v1, v2, v3, v4, EPSILON)) {
        // 检查两条边是否有重叠部分
        if (doEdgesOverlap(v1, v2, v3, v4, EPSILON)) {
          return true;
        }
      }
    }
  }
  
  return false;
}

/**
 * 检查两条边是否共线
 * @param v1 第一条边的起点
 * @param v2 第一条边的终点
 * @param v3 第二条边的起点
 * @param v4 第二条边的终点
 * @param epsilon 误差容忍度
 * @returns 如果两条边共线，返回true；否则返回false
 */
function areEdgesCollinear(
  v1: THREE.Vector3, 
  v2: THREE.Vector3, 
  v3: THREE.Vector3, 
  v4: THREE.Vector3, 
  epsilon: number
): boolean {
  // 计算方向向量
  const dir1 = new THREE.Vector3();
  (dir1 as any).subVectors(v2, v1);
  (dir1 as any).normalize();
  
  const dir2 = new THREE.Vector3();
  (dir2 as any).subVectors(v4, v3);
  (dir2 as any).normalize();
  
  // 检查方向向量是否平行（同向或反向）
  const dot = Math.abs((dir1 as any).dot(dir2));
  const areParallel = Math.abs(dot - 1) < epsilon;
  
  if (!areParallel) return false;
  
  // 检查点v3是否在由v1和v2定义的直线上
  // 计算v1到v3的向量
  const v1ToV3 = new THREE.Vector3();
  (v1ToV3 as any).subVectors(v3, v1);
  
  // 如果v1ToV3和dir1平行，则v3在直线上
  const v1ToV3Normalized = v1ToV3.clone();
  (v1ToV3Normalized as any).normalize();
  const v3OnLine = Math.abs(Math.abs((v1ToV3Normalized as any).dot(dir1)) - 1) < epsilon;
  
  return v3OnLine;
}

/**
 * 检查两条共线的边是否有重叠部分
 * @param v1 第一条边的起点
 * @param v2 第一条边的终点
 * @param v3 第二条边的起点
 * @param v4 第二条边的终点
 * @param epsilon 误差容忍度
 * @returns 如果两条边有重叠部分，返回true；否则返回false
 */
function doEdgesOverlap(
  v1: THREE.Vector3, 
  v2: THREE.Vector3, 
  v3: THREE.Vector3, 
  v4: THREE.Vector3, 
  epsilon: number
): boolean {
  // 计算方向向量
  const dir = new THREE.Vector3();
  (dir as any).subVectors(v2, v1);
  (dir as any).normalize();
  
  // 将所有点投影到这个方向上
  const proj1 = (dir as any).dot(v1);
  const proj2 = (dir as any).dot(v2);
  const proj3 = (dir as any).dot(v3);
  const proj4 = (dir as any).dot(v4);
  
  // 确保proj1 <= proj2和proj3 <= proj4
  const min1 = Math.min(proj1, proj2);
  const max1 = Math.max(proj1, proj2);
  const min2 = Math.min(proj3, proj4);
  const max2 = Math.max(proj3, proj4);
  
  // 检查投影是否有重叠
  // 两条线段有重叠的条件：一条线段的最小值小于等于另一条线段的最大值，且一条线段的最大值大于等于另一条线段的最小值
  return max1 >= min2 - epsilon && min1 <= max2 + epsilon;
}

/**
 * 检查两个面是否有交集
 * @param face1 第一个面
 * @param face2 第二个面
 * @returns 如果两个面有交集，返回交集多边形的顶点；否则返回null
 */
export function getFacesIntersection(face1: Face, face2: Face): THREE.Vector3[] | null {
  // 如果两个面不共面，则没有交集
  if (!areFacesCoplanar(face1, face2)) return null;
  
  // 使用Sutherland-Hodgman算法计算两个多边形的交集
  // 将face1作为裁剪多边形，face2作为被裁剪多边形
  
  // 首先，将两个面的顶点投影到2D平面上
  // 选择最适合的投影平面（根据法向量）
  const normal = face1.normal;
  let projectionPlane: 'xy' | 'yz' | 'xz';
  
  // 选择最适合的投影平面（根据法向量的主要分量）
  const absX = Math.abs(normal.x);
  const absY = Math.abs(normal.y);
  const absZ = Math.abs(normal.z);
  
  if (absX >= absY && absX >= absZ) {
    projectionPlane = 'yz'; // 投影到YZ平面
  } else if (absY >= absX && absY >= absZ) {
    projectionPlane = 'xz'; // 投影到XZ平面
  } else {
    projectionPlane = 'xy'; // 投影到XY平面
  }
  
  // 投影顶点到2D
  const project = (v: THREE.Vector3): [number, number] => {
    switch (projectionPlane) {
      case 'xy': return [v.x, v.y];
      case 'yz': return [v.y, v.z];
      case 'xz': return [v.x, v.z];
    }
  };
  
  // 反投影2D点到3D
  const unproject = (p: [number, number], baseVertex: THREE.Vector3): THREE.Vector3 => {
    switch (projectionPlane) {
      case 'xy': return new THREE.Vector3(p[0], p[1], baseVertex.z);
      case 'yz': return new THREE.Vector3(baseVertex.x, p[0], p[1]);
      case 'xz': return new THREE.Vector3(p[0], baseVertex.y, p[1]);
    }
  };
  
  // 将面的顶点投影到2D
  const vertices1_2D = face1.vertices.map(project);
  const vertices2_2D = face2.vertices.map(project);
  
  // 使用一个2D多边形裁剪库来计算交集
  // 这里使用简化的方法：检查每个顶点是否在另一个多边形内部
  
  // 检查点是否在多边形内部（射线法）
  const isPointInPolygon = (point: [number, number], polygon: [number, number][]): boolean => {
    const [x, y] = point;
    let inside = false;
    
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const [xi, yi] = polygon[i];
      const [xj, yj] = polygon[j];
      
      const intersect = ((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }
    
    return inside;
  };
  
  // 检查点是否在多边形边界上
  const isPointOnPolygonEdge = (point: [number, number], polygon: [number, number][]): boolean => {
    const [x, y] = point;
    const EPSILON = 0.0001;
    
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
      const [xi, yi] = polygon[i];
      const [xj, yj] = polygon[j];
      
      // 计算点到线段的距离
      const dx = xj - xi;
      const dy = yj - yi;
      const length = Math.sqrt(dx * dx + dy * dy);
      
      if (length < EPSILON) continue; // 忽略长度为0的线段
      
      // 计算点到线段的距离
      const t = ((x - xi) * dx + (y - yi) * dy) / (length * length);
      
      if (t < 0 || t > 1) continue; // 点的投影不在线段上
      
      const projX = xi + t * dx;
      const projY = yi + t * dy;
      const distance = Math.sqrt((x - projX) * (x - projX) + (y - projY) * (y - projY));
      
      if (distance < EPSILON) return true;
    }
    
    return false;
  };
  
  // 计算线段交点
  const lineIntersection = (
    a: [number, number], 
    b: [number, number], 
    c: [number, number], 
    d: [number, number]
  ): [number, number] | null => {
    const denominator = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0]);
    if (Math.abs(denominator) < 0.0001) return null; // 平行线
    
    const ua = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / denominator;
    const ub = ((a[0] - c[0]) * (b[1] - a[1]) - (a[1] - c[1]) * (b[0] - a[0])) / -denominator;
    
    // 允许端点相交
    const EPSILON = 0.0001;
    if (ua < -EPSILON || ua > 1 + EPSILON || ub < -EPSILON || ub > 1 + EPSILON) return null; // 交点不在线段上
    
    // 处理端点相交的情况
    const x = a[0] + ua * (b[0] - a[0]);
    const y = a[1] + ua * (b[1] - a[1]);
    
    return [x, y];
  };
  
  // 收集所有可能的交点
  const intersectionPoints: [number, number][] = [];
  
  // 添加位于另一个多边形内部的顶点
  vertices1_2D.forEach(v => {
    if (isPointInPolygon(v, vertices2_2D) || isPointOnPolygonEdge(v, vertices2_2D)) {
      intersectionPoints.push(v);
    }
  });
  
  vertices2_2D.forEach(v => {
    if (isPointInPolygon(v, vertices1_2D) || isPointOnPolygonEdge(v, vertices1_2D)) {
      intersectionPoints.push(v);
    }
  });
  
  // 添加边的交点
  for (let i = 0; i < vertices1_2D.length; i++) {
    const a = vertices1_2D[i];
    const b = vertices1_2D[(i + 1) % vertices1_2D.length];
    
    for (let j = 0; j < vertices2_2D.length; j++) {
      const c = vertices2_2D[j];
      const d = vertices2_2D[(j + 1) % vertices2_2D.length];
      
      const intersection = lineIntersection(a, b, c, d);
      if (intersection) {
        intersectionPoints.push(intersection);
      }
    }
  }
  
  // 如果没有交点，则没有交集
  if (intersectionPoints.length < 3) return null;
  
  // 移除重复点
  const uniquePoints: [number, number][] = [];
  const EPSILON = 0.0001;
  
  for (let i = 0; i < intersectionPoints.length; i++) {
    const p = intersectionPoints[i];
    let isDuplicate = false;
    
    for (let j = 0; j < uniquePoints.length; j++) {
      const existing = uniquePoints[j];
      const dx = p[0] - existing[0];
      const dy = p[1] - existing[1];
      const distSquared = dx * dx + dy * dy;
      
      if (distSquared < EPSILON * EPSILON) {
        isDuplicate = true;
        break;
      }
    }
    
    if (!isDuplicate) {
      uniquePoints.push(p);
    }
  }
  
  // 如果不足3个点，则没有有效的交集
  if (uniquePoints.length < 3) return null;
  
  // 对交点进行排序（按照极角排序）
  // 首先计算中心点
  const center: [number, number] = [0, 0];
  uniquePoints.forEach(p => {
    center[0] += p[0];
    center[1] += p[1];
  });
  center[0] /= uniquePoints.length;
  center[1] /= uniquePoints.length;
  
  // 按照极角排序
  uniquePoints.sort((a, b) => {
    return Math.atan2(a[1] - center[1], a[0] - center[0]) - 
           Math.atan2(b[1] - center[1], b[0] - center[0]);
  });
  
  // 将2D点反投影回3D
  // 使用face1的第一个顶点作为基准点
  const baseVertex = face1.vertices[0];
  const intersection3D = uniquePoints.map(p => unproject(p, baseVertex));
  
  return intersection3D;
}

/**
 * 查找所有面的交集
 * @param faces 所有面
 * @returns 交集面数组
 */
export function findAllFaceIntersections(faces: Face[]): Face[] {
  const intersectionFaces: Face[] = [];
  const processedPairs = new Set<string>();
  
  // 初始化每个面的childIntersections数组
  faces.forEach(face => {
    face.childIntersections = [];
  });
  
  // 遍历所有面对
  for (let i = 0; i < faces.length; i++) {
    for (let j = i + 1; j < faces.length; j++) {
      const face1 = faces[i];
      const face2 = faces[j];
      
      // 检查两个面是否属于同一个立方体
      const cubeIndex1 = Math.floor(i / 6);
      const cubeIndex2 = Math.floor(j / 6);
      
      // 如果两个面属于同一个立方体，则跳过
      if (cubeIndex1 === cubeIndex2) continue;
      
      // 创建唯一的面对标识符
      const pairId = `${i}-${j}`;
      if (processedPairs.has(pairId)) continue;
      processedPairs.add(pairId);
      
      // 计算交集
      const intersectionVertices = getFacesIntersection(face1, face2);
      
      // 如果有交集，则创建一个新的面
      if (intersectionVertices && intersectionVertices.length >= 3) {
        // 计算面积，过滤掉面积太小的交集面
        const area = calculatePolygonArea(intersectionVertices);
        
        // 使用更小的面积阈值，以捕获更多的交集面
        const AREA_THRESHOLD = 0.00001;
        if (area < AREA_THRESHOLD) {
          // console.log(`跳过面积太小的交集面: ${area}`);
          continue;
        }
        
        // 创建交集面
        const intersectionFace: Face = {
          vertices: intersectionVertices,
          normal: face1.normal.clone(), // 使用第一个面的法向量
          color: 0xffff00, // 黄色
          parentFaces: [i, j]
        };
        
        // 添加到交集面数组
        const intersectionIndex = intersectionFaces.length;
        intersectionFaces.push(intersectionFace);
        
        // 更新原始面的childIntersections属性
        if (!face1.childIntersections) face1.childIntersections = [];
        if (!face2.childIntersections) face2.childIntersections = [];
        
        face1.childIntersections.push(intersectionIndex);
        face2.childIntersections.push(intersectionIndex);
        
        // 输出调试信息
        // console.log(`找到交集面 - 立方体 ${cubeIndex1} 和 ${cubeIndex2}, 顶点数: ${intersectionVertices.length}, 面积: ${area}`);
      }
    }
  }
  
  // 尝试使用不同的方法计算交集
  // 这是一个备用方法，用于捕获可能被主方法遗漏的交集
  findIntersectionsByProjection(faces, intersectionFaces);
  
  return intersectionFaces;
}

/**
 * 使用投影方法查找交集面
 * 这是一个备用方法，用于捕获可能被主方法遗漏的交集
 * @param faces 所有面
 * @param intersectionFaces 已找到的交集面数组
 */
function findIntersectionsByProjection(faces: Face[], intersectionFaces: Face[]): void {
  // 按法向量分组
  const faceGroups: Map<string, Face[]> = new Map();
  
  // 将面按法向量分组
  faces.forEach((face, index) => {
    const normal = face.normal;
    const key = `${Math.round(normal.x)},${Math.round(normal.y)},${Math.round(normal.z)}`;
    
    if (!faceGroups.has(key)) {
      faceGroups.set(key, []);
    }
    
    faceGroups.get(key)!.push(face);
  });
  
  // 处理每个法向量组
  faceGroups.forEach((groupFaces, normalKey) => {
    // 如果组内只有一个面，则跳过
    if (groupFaces.length <= 1) return;
    
    // console.log(`处理法向量组 ${normalKey}，包含 ${groupFaces.length} 个面`);
    
    // 检查组内的面是否共面
    for (let i = 0; i < groupFaces.length; i++) {
      for (let j = i + 1; j < groupFaces.length; j++) {
        const face1 = groupFaces[i];
        const face2 = groupFaces[j];
        
        // 获取面的索引
        const faceIndex1 = faces.indexOf(face1);
        const faceIndex2 = faces.indexOf(face2);
        
        // 检查两个面是否属于同一个立方体
        const cubeIndex1 = Math.floor(faceIndex1 / 6);
        const cubeIndex2 = Math.floor(faceIndex2 / 6);
        
        // 如果两个面属于同一个立方体，则跳过
        if (cubeIndex1 === cubeIndex2) continue;
        
        // 检查两个面是否共面
        if (!areFacesCoplanar(face1, face2)) continue;
        
        // 计算交集
        const intersectionVertices = getFacesIntersection(face1, face2);
        
        // 如果有交集，则创建一个新的面
        if (intersectionVertices && intersectionVertices.length >= 3) {
          // 计算面积
          const area = calculatePolygonArea(intersectionVertices);
          
          // 使用更小的面积阈值
          const AREA_THRESHOLD = 0.00001;
          if (area < AREA_THRESHOLD) continue;
          
          // 检查是否与已有的交集面重复
          let isDuplicate = false;
          for (const existingFace of intersectionFaces) {
            if (areFacesEqual(existingFace, { vertices: intersectionVertices, normal: face1.normal })) {
              isDuplicate = true;
              break;
            }
          }
          
          if (isDuplicate) continue;
          
          // 创建交集面
          const intersectionFace: Face = {
            vertices: intersectionVertices,
            normal: face1.normal.clone(),
            color: 0xff9900, // 橙色，区别于主方法找到的交集面
            parentFaces: [faceIndex1, faceIndex2]
          };
          
          // 添加到交集面数组
          const intersectionIndex = intersectionFaces.length;
          intersectionFaces.push(intersectionFace);
          
          // 更新原始面的childIntersections属性
          if (!face1.childIntersections) face1.childIntersections = [];
          if (!face2.childIntersections) face2.childIntersections = [];
          
          face1.childIntersections.push(intersectionIndex);
          face2.childIntersections.push(intersectionIndex);
          
          // console.log(`备用方法找到交集面 - 顶点数: ${intersectionVertices.length}, 面积: ${area}`);
        }
      }
    }
  });
}

/**
 * 检查两个面是否相等
 * @param face1 第一个面
 * @param face2 第二个面
 * @returns 如果两个面相等，返回true；否则返回false
 */
function areFacesEqual(face1: Face, face2: Face): boolean {
  // 检查法向量是否相同
  const normalEqual = Math.abs(face1.normal.x - face2.normal.x) < 0.01 &&
                      Math.abs(face1.normal.y - face2.normal.y) < 0.01 &&
                      Math.abs(face1.normal.z - face2.normal.z) < 0.01;
  
  if (!normalEqual) return false;
  
  // 检查顶点数量是否相同
  if (face1.vertices.length !== face2.vertices.length) return false;
  
  // 计算中心点
  const center1 = calculateCenter(face1.vertices);
  const center2 = calculateCenter(face2.vertices);
  
  // 检查中心点是否接近
  const centerEqual = Math.abs(center1.x - center2.x) < 0.1 &&
                      Math.abs(center1.y - center2.y) < 0.1 &&
                      Math.abs(center1.z - center2.z) < 0.1;
  
  return centerEqual;
}

/**
 * 计算顶点的中心点
 * @param vertices 顶点数组
 * @returns 中心点
 */
function calculateCenter(vertices: THREE.Vector3[]): THREE.Vector3 {
  const center = new THREE.Vector3(0, 0, 0);
  
  vertices.forEach(v => {
    center.x += v.x;
    center.y += v.y;
    center.z += v.z;
  });
  
  center.x /= vertices.length;
  center.y /= vertices.length;
  center.z /= vertices.length;
  
  return center;
}

/**
 * 计算多边形的面积
 * @param vertices 多边形的顶点
 * @returns 面积
 */
function calculatePolygonArea(vertices: THREE.Vector3[]): number {
  if (vertices.length < 3) return 0;
  
  // 选择投影平面
  const normal = calculatePolygonNormal(vertices);
  let projectionPlane: 'xy' | 'yz' | 'xz';
  
  const absX = Math.abs(normal.x);
  const absY = Math.abs(normal.y);
  const absZ = Math.abs(normal.z);
  
  if (absX >= absY && absX >= absZ) {
    projectionPlane = 'yz'; // 投影到YZ平面
  } else if (absY >= absX && absY >= absZ) {
    projectionPlane = 'xz'; // 投影到XZ平面
  } else {
    projectionPlane = 'xy'; // 投影到XY平面
  }
  
  // 投影顶点到2D
  const vertices2D: [number, number][] = vertices.map(v => {
    switch (projectionPlane) {
      case 'xy': return [v.x, v.y];
      case 'yz': return [v.y, v.z];
      case 'xz': return [v.x, v.z];
    }
  });
  
  // 使用叉积计算面积
  let area = 0;
  for (let i = 0; i < vertices2D.length; i++) {
    const j = (i + 1) % vertices2D.length;
    area += vertices2D[i][0] * vertices2D[j][1];
    area -= vertices2D[j][0] * vertices2D[i][1];
  }
  
  return Math.abs(area) / 2;
}

/**
 * 计算多边形的法向量
 * @param vertices 多边形的顶点
 * @returns 法向量
 */
function calculatePolygonNormal(vertices: THREE.Vector3[]): THREE.Vector3 {
  if (vertices.length < 3) return new THREE.Vector3(0, 1, 0);
  
  // 使用前三个点计算法向量
  const v1 = new THREE.Vector3();
  (v1 as any).subVectors(vertices[1], vertices[0]);
  
  const v2 = new THREE.Vector3();
  (v2 as any).subVectors(vertices[2], vertices[0]);
  
  const normal = new THREE.Vector3();
  (normal as any).crossVectors(v1, v2);
  (normal as any).normalize();
  
  return normal;
}

/**
 * 2D点
 */
interface Point2D {
  x: number;
  y: number;
}

/**
 * 2D矩形
 */
interface Rect2D {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

/**
 * 将3D面投影到2D平面
 * @param face 3D面
 * @returns 投影后的2D矩形和投影信息
 */
function projectFaceTo2D(face: Face): { rect: Rect2D, projectionInfo: any } {
  const normal = face.normal;
  // 确定投影平面
  let projectionPlane: 'xy' | 'yz' | 'xz';
  const absX = Math.abs(normal.x);
  const absY = Math.abs(normal.y);
  const absZ = Math.abs(normal.z);
  
  // 根据法向量选择最合适的投影平面
  if (absX >= absY && absX >= absZ) {
    projectionPlane = 'yz'; // 投影到YZ平面
  } else if (absY >= absX && absY >= absZ) {
    projectionPlane = 'xz'; // 投影到XZ平面
  } else {
    projectionPlane = 'xy'; // 投影到XY平面
  }
  
  // 投影顶点到2D，确保x坐标总是对应"横向"
  const vertices2D = face.vertices.map(v => {
    switch (projectionPlane) {
      case 'xy': return { x: v.x, y: v.y }; // x是横向
      case 'yz': return { x: v.z, y: v.y }; // z是横向
      case 'xz': return { x: v.z, y: v.x }; // z是横向
    }
  });
  
  // 计算包围盒
  let minX = Infinity, minY = Infinity;
  let maxX = -Infinity, maxY = -Infinity;
  
  vertices2D.forEach(v => {
    minX = Math.min(minX, v.x);
    minY = Math.min(minY, v.y);
    maxX = Math.max(maxX, v.x);
    maxY = Math.max(maxY, v.y);
  });
  
  // 创建2D矩形
  const rect: Rect2D = {
    x0: minX,
    y0: minY,
    x1: maxX,
    y1: maxY
  };
  
  return {
    rect,
    projectionInfo: {
      plane: projectionPlane,
      vertices2D,
      normal,
      // 存储一个顶点用于反投影
      baseVertex: face.vertices[0]
    }
  };
}

/**
 * 计算区间的交集
 * @param intervals 区间数组
 * @returns 合并后的区间数组
 */
function mergeIntervals(intervals: [number, number][]): [number, number][] {
  if (intervals.length === 0) return [];
  
  // 按起始点排序
  const sortedIntervals = [...intervals].sort((a, b) => a[0] - b[0]);
  const merged: [number, number][] = [sortedIntervals[0]];
  
  for (let i = 1; i < sortedIntervals.length; i++) {
    const current = sortedIntervals[i];
    const last = merged[merged.length - 1];
    
    if (current[0] <= last[1]) {
      // 区间重叠，合并
      last[1] = Math.max(last[1], current[1]);
    } else {
      // 区间不重叠，添加新区间
      merged.push(current);
    }
  }
  
  return merged;
}

/**
 * 计算区间的差集
 * @param base 基础区间
 * @param covers 覆盖区间数组
 * @returns 未被覆盖的区间数组
 */
function subtractIntervals(base: [number, number], covers: [number, number][]): [number, number][] {
  const [baseStart, baseEnd] = base;
  const mergedCovers = mergeIntervals(covers);
  
  const uncovered: [number, number][] = [];
  let currentStart = baseStart;
  
  for (const [covStart, covEnd] of mergedCovers) {
    if (covStart > currentStart) {
      uncovered.push([currentStart, covStart]);
    }
    currentStart = Math.max(currentStart, covEnd);
  }
  
  if (currentStart < baseEnd) {
    uncovered.push([currentStart, baseEnd]);
  }
  
  return uncovered;
}

/**
 * 计算2D矩形减去子矩形后的剩余区域
 * @param bigRect 大矩形
 * @param subRects 子矩形数组
 * @returns 剩余区域的多边形顶点数组
 */
function computeRemainingArea(bigRect: Rect2D, subRects: Rect2D[]): Point2D[][] {
  // 收集横向边界 - 始终使用x轴作为横向分割
  const horizontalEdges = new Set<number>([bigRect.x0, bigRect.x1]);
  for (const rect of subRects) {
    horizontalEdges.add(rect.x0);
    horizontalEdges.add(rect.x1);
  }
  
  // 排序并去重
  const sortedX = Array.from(horizontalEdges).sort((a, b) => a - b);
  
  const strips: [number, number, number, number][] = [];
  
  // 处理每个横向条带
  for (let i = 0; i < sortedX.length - 1; i++) {
    const xStart = sortedX[i];
    const xEnd = sortedX[i + 1];
    
    if (xStart >= bigRect.x1 || xEnd <= bigRect.x0) {
      continue; // 超出大矩形范围
    }
    
    // 筛选横跨当前横向条带的子矩形
    const spanning: [number, number][] = [];
    for (const rect of subRects) {
      if (rect.x0 <= xStart && rect.x1 >= xEnd) {
        spanning.push([rect.y0, rect.y1]);
      }
    }
    
    // 计算未被覆盖的y区间
    const uncovered = subtractIntervals([bigRect.y0, bigRect.y1], spanning);
    
    // 生成矩形条
    for (const [low, high] of uncovered) {
      strips.push([xStart, low, xEnd, high]);
    }
  }
  
  // 合并相邻矩形条 - 只合并x方向相邻的条带
  strips.sort((a, b) => {
    if (a[1] !== b[1]) return a[1] - b[1]; // 按底边y排序
    if (a[3] !== b[3]) return a[3] - b[3]; // 按顶边y排序
    return a[0] - b[0]; // 按左边x排序
  });
  
  const merged: [number, number, number, number][] = [];
  let current: [number, number, number, number] | null = null;
  
  for (const strip of strips) {
    if (current === null) {
      current = strip;
    } else {
      // 显式声明变量类型，避免循环引用类型错误
      const xs1: number = current[0];
      const ys1: number = current[1];
      const xe1: number = current[2];
      const ye1: number = current[3];
      
      const xs2: number = strip[0];
      const ys2: number = strip[1];
      const xe2: number = strip[2];
      const ye2: number = strip[3];
      
      if (ys1 === ys2 && ye1 === ye2 && Math.abs(xs1 - xs2) < 0.001) {
        // 可以合并的矩形条 - 只合并x方向相邻的条带
        current = [xs1, ys1, xe2, ye1];
      } else {
        merged.push(current);
        current = strip;
      }
    }
  }
  
  if (current !== null) {
    merged.push(current);
  }
  
  // 转换为多边形顶点列表
  const result: Point2D[][] = [];
  for (const [xs, ys, xe, ye] of merged) {
    const polygon = [
      { x: xs, y: ys },
      { x: xe, y: ys },
      { x: xe, y: ye },
      { x: xs, y: ye }
    ];
    result.push(polygon);
  }
  
  return result;
}

/**
 * 将2D点转回3D空间
 * @param point 2D点
 * @param projectionInfo 投影信息
 * @returns 3D点
 */
function unproject2DPoint(point: Point2D, projectionInfo: any): THREE.Vector3 {
  const { plane, baseVertex } = projectionInfo;
  
  switch (plane) {
    case 'xy':
      return new THREE.Vector3(point.x, point.y, baseVertex.z);
    case 'yz':
      return new THREE.Vector3(baseVertex.x, point.y, point.x);
    case 'xz':
      return new THREE.Vector3(point.y, baseVertex.y, point.x);
    default:
      // 添加默认返回，避免类型错误
      return new THREE.Vector3();
  }
}

/**
 * 根据法向量确定面的颜色
 * @param normal 面的法向量
 * @returns 颜色值（十六进制）
 */
function getColorByNormal(normal: THREE.Vector3): number {
  // 四舍五入法向量的分量，以确定主要方向
  const x = Math.round(normal.x);
  const y = Math.round(normal.y);
  const z = Math.round(normal.z);
  
  // 根据主要方向分配颜色
  if (x === -1 && y === 0 && z === 0) return 0xff66ff; // 左面 (-X) - 紫色
  if (x === 1 && y === 0 && z === 0) return 0x66ffff;  // 右面 (+X) - 青色
  if (x === 0 && y === -1 && z === 0) return 0xff6666; // 下面 (-Y) - 红色
  if (x === 0 && y === 1 && z === 0) return 0xffff66;  // 上面 (+Y) - 黄色
  if (x === 0 && y === 0 && z === -1) return 0x6666ff; // 后面 (-Z) - 蓝色
  if (x === 0 && y === 0 && z === 1) return 0x66ff66;  // 前面 (+Z) - 绿色
  
  // 默认颜色（浅蓝色）
  return 0x00aaff;
}

/**
 * 计算立方体面被交集面裁剪后的剩余区域
 * @param originalFace 原始立方体面
 * @param intersectionFaces 与原始面共面的交集面数组
 * @returns 裁剪后的剩余区域的多边形数组
 */
export function computeClippedFace(originalFace: Face, intersectionFaces: Face[]): Face[] {
  // 投影到2D
  const { rect: bigRect, projectionInfo } = projectFaceTo2D(originalFace);
  
  // 投影交集面到2D
  const subRects: Rect2D[] = [];
  for (const face of intersectionFaces) {
    // 确保交集面与原始面共面
    if (areFacesCoplanar(originalFace, face)) {
      const { rect } = projectFaceTo2D(face);
      subRects.push(rect);
    }
  }
  
  // 计算剩余区域
  const remainingPolygons = computeRemainingArea(bigRect, subRects);
  
  // 将2D多边形转回3D
  const clippedFaces: Face[] = [];
  
  // 设置面积阈值，小于此值的裁剪面将被忽略
  const CLIPPED_FACE_AREA_THRESHOLD = 0.01;
  
  for (const polygon of remainingPolygons) {
    const vertices3D = polygon.map(point => unproject2DPoint(point, projectionInfo));
    
    // 计算面积
    const area = calculatePolygonArea(vertices3D);
    
    // 如果面积小于阈值，则跳过该面
    if (area < CLIPPED_FACE_AREA_THRESHOLD) {
      console.log(`跳过面积太小的裁剪面: ${area.toFixed(6)}`);
      continue;
    }
    
    // 根据法向量确定颜色
    const faceColor = getColorByNormal(originalFace.normal);
    
    // 创建裁剪后的面
    const clippedFace: Face = {
      vertices: vertices3D,
      normal: originalFace.normal.clone(),
      color: faceColor, // 使用根据法向量确定的颜色
      parentFace: originalFace.parentFace
    };
    
    clippedFaces.push(clippedFace);
  }
  
  return clippedFaces;
}

/**
 * 计算所有立方体面被裁剪后的面
 * @param originalFaces 原始立方体面数组
 * @param intersectionFaces 交集面数组
 * @returns 裁剪后的面数组
 */
export function computeAllClippedFaces(originalFaces: Face[], intersectionFaces: Face[]): Face[] {
  const clippedFaces: Face[] = [];
  
  for (let i = 0; i < originalFaces.length; i++) {
    const face = originalFaces[i];
    
    // 检查是否有交集面
    if (face.childIntersections && face.childIntersections.length > 0) {
      // 收集与该面共面的交集面
      const relatedIntersections = face.childIntersections
        .map(index => intersectionFaces[index])
        .filter(intersectionFace => areFacesCoplanar(face, intersectionFace));
      
      if (relatedIntersections.length > 0) {
        // 计算裁剪后的面
        const clipped = computeClippedFace(face, relatedIntersections);
        
        // 为每个裁剪面添加原始面信息
        clipped.forEach(clippedFace => {
          clippedFace.parentFace = i; // 记录原始面的索引
        });
        
        clippedFaces.push(...clipped);
      } else {
        // 没有共面的交集面，保持原样
        // 根据法向量确定颜色
        const faceColor = getColorByNormal(face.normal);
        
        const clonedFace = { 
          ...face, 
          color: faceColor, // 使用根据法向量确定的颜色
          parentFace: i // 记录原始面的索引
        };
        clippedFaces.push(clonedFace);
      }
    } else {
      // 没有交集面，保持原样
      // 根据法向量确定颜色
      const faceColor = getColorByNormal(face.normal);
      
      const clonedFace = { 
        ...face, 
        color: faceColor, // 使用根据法向量确定的颜色
        parentFace: i // 记录原始面的索引
      };
      clippedFaces.push(clonedFace);
    }
  }
  
  return clippedFaces;
}

/**
 * 将具有相同原始面且边缘相连的裁剪面分组
 * @param clippedFaces 裁剪面数组
 * @returns 分组后的裁剪面索引数组，每个子数组表示一个组
 */
export function groupConnectedClippedFaces(clippedFaces: Face[]): number[][] {
  // 按原始面分组
  const facesByParent: Map<number, number[]> = new Map();
  
  // 首先按照parentFace进行初步分组
  clippedFaces.forEach((face, index) => {
    if (face.parentFace === undefined) return;
    
    if (!facesByParent.has(face.parentFace)) {
      facesByParent.set(face.parentFace, []);
    }
    
    facesByParent.get(face.parentFace)!.push(index);
  });
  
  // 最终的分组结果
  const groups: number[][] = [];
  
  // 对每个原始面的裁剪面进行连通性分析
  facesByParent.forEach((faceIndices) => {
    // 如果只有一个裁剪面，直接作为一个组
    if (faceIndices.length === 1) {
      groups.push([...faceIndices]);
      return;
    }
    
    // 创建邻接表
    const adjacencyList: Map<number, number[]> = new Map();
    faceIndices.forEach(index => {
      adjacencyList.set(index, []);
    });
    
    // 检查每对裁剪面是否相连
    for (let i = 0; i < faceIndices.length; i++) {
      for (let j = i + 1; j < faceIndices.length; j++) {
        const index1 = faceIndices[i];
        const index2 = faceIndices[j];
        const face1 = clippedFaces[index1];
        const face2 = clippedFaces[index2];
        
        // 检查两个面是否通过边连接
        if (areFacesConnectedByEdge(face1, face2)) {
          adjacencyList.get(index1)!.push(index2);
          adjacencyList.get(index2)!.push(index1);
        }
      }
    }
    
    // 使用DFS找出所有连通分量
    const visited = new Set<number>();
    
    // DFS函数
    function dfs(node: number, component: number[]) {
      visited.add(node);
      component.push(node);
      
      for (const neighbor of adjacencyList.get(node) || []) {
        if (!visited.has(neighbor)) {
          dfs(neighbor, component);
        }
      }
    }
    
    // 找出所有连通分量
    for (const index of faceIndices) {
      if (!visited.has(index)) {
        const component: number[] = [];
        dfs(index, component);
        groups.push(component);
      }
    }
  });
  
  return groups;
} 