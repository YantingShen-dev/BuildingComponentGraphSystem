declare module 'three' {
  export class Scene {
    background: Color;
    add(object: Object3D): this;
    remove(object: Object3D): this;
    children: Object3D[];
  }
  
  export class PerspectiveCamera extends Object3D {
    constructor(fov: number, aspect: number, near: number, far: number);
    aspect: number;
    position: Vector3;
    quaternion: Quaternion;
    updateProjectionMatrix(): void;
    lookAt(x: number, y: number, z: number): void;
    lookAt(target: Vector3): void;
  }
  
  export class WebGLRenderer {
    constructor(parameters?: { canvas?: HTMLCanvasElement; antialias?: boolean });
    setSize(width: number, height: number): void;
    setPixelRatio(value: number): void;
    render(scene: Scene, camera: Camera): void;
    domElement: HTMLCanvasElement;
    dispose(): void;
  }
  
  export class Color {
    constructor(color: number | string);
    set(color: number | string): this;
  }
  
  export class Vector2 {
    constructor(x?: number, y?: number);
    x: number;
    y: number;
    set(x: number, y: number): this;
    copy(v: Vector2): this;
    subVectors(a: Vector2, b: Vector2): this;
  }
  
  export class Vector3 {
    constructor(x?: number, y?: number, z?: number);
    x: number;
    y: number;
    z: number;
    set(x: number, y: number, z: number): this;
    copy(v: Vector3): this;
    clone(): Vector3;
    multiply(v: Vector3): this;
    multiplyScalar(s: number): this;
    addScaledVector(v: Vector3, s: number): this;
    applyQuaternion(q: Quaternion): this;
  }
  
  export class Raycaster {
    constructor();
    setFromCamera(coords: Vector2, camera: Camera): void;
    intersectObjects(objects: Object3D[], recursive?: boolean): Intersection[];
    params: {
      Line: { threshold: number };
      Points: { threshold: number };
      Mesh: { threshold: number };
    };
  }
  
  export interface Intersection {
    distance: number;
    point: Vector3;
    face: Face;
    faceIndex?: number;
    object: Object3D;
  }
  
  export interface Face {
    a: number;
    b: number;
    c: number;
    normal: Vector3;
  }
  
  export class Object3D {
    position: Vector3;
    userData: any;
    parent: Object3D | null;
    children: Object3D[];
    add(object: Object3D): this;
    remove(object: Object3D): this;
  }
  
  export class Group extends Object3D {
    constructor();
  }
  
  export class Mesh extends Object3D {
    constructor(geometry?: BufferGeometry, material?: Material | Material[]);
    geometry: BufferGeometry;
    material: Material | Material[];
  }
  
  export class GridHelper extends Object3D {
    constructor(size?: number, divisions?: number);
    material: Material | Material[];
  }
  
  export class BoxGeometry extends BufferGeometry {
    constructor(width?: number, height?: number, depth?: number);
  }
  
  export class SphereGeometry extends BufferGeometry {
    constructor(radius?: number, widthSegments?: number, heightSegments?: number);
  }
  
  export class EdgesGeometry extends BufferGeometry {
    constructor(geometry: BufferGeometry);
  }
  
  export class BufferGeometry {
    constructor();
    boundingBox: Box3 | null;
    computeBoundingBox(): void;
  }
  
  export class Material {
    constructor();
    transparent: boolean;
    opacity: number;
    dispose(): void;
  }
  
  export class MeshBasicMaterial extends Material {
    constructor(parameters?: { color?: number | string; transparent?: boolean; opacity?: number });
    color: Color;
  }
  
  export class MeshStandardMaterial extends Material {
    constructor(parameters?: { color?: number | string; transparent?: boolean; opacity?: number });
    color: Color;
  }
  
  export class LineBasicMaterial extends Material {
    constructor(parameters?: { color?: number | string; linewidth?: number });
    color: Color;
    linewidth: number;
  }
  
  export class AmbientLight extends Light {
    constructor(color?: number | string, intensity?: number);
  }
  
  export class DirectionalLight extends Light {
    constructor(color?: number | string, intensity?: number);
    position: Vector3;
  }
  
  export class Light extends Object3D {
    constructor(color?: number | string, intensity?: number);
  }
  
  export class Camera extends Object3D {
    constructor();
    lookAt(x: number, y: number, z: number): void;
    lookAt(target: Vector3): void;
  }
  
  export class AxesHelper extends Object3D {
    constructor(size?: number);
  }
  
  export class Quaternion {
    constructor(x?: number, y?: number, z?: number, w?: number);
    x: number;
    y: number;
    z: number;
    w: number;
  }
  
  export class Texture {
    constructor();
  }
  
  export class CanvasTexture extends Texture {
    constructor(canvas: HTMLCanvasElement);
  }
  
  export class LineSegments extends Object3D {
    constructor(geometry?: BufferGeometry, material?: Material);
    geometry: BufferGeometry;
    material: Material;
  }
  
  export class Box3 {
    constructor();
    getSize(target: Vector3): Vector3;
  }
}

declare module 'three/examples/jsm/controls/OrbitControls' {
  import { Camera, Object3D, Vector3 } from 'three';
  
  export class OrbitControls {
    constructor(camera: Camera, domElement?: HTMLElement);
    
    enabled: boolean;
    enableDamping: boolean;
    enablePan: boolean;
    enableRotate: boolean;
    enableZoom: boolean;
    
    mouseButtons: {
      LEFT: number | null;
      MIDDLE: number | null;
      RIGHT: number | null;
    };
    
    target: Vector3;
    
    update(): void;
    dispose(): void;
  }
}