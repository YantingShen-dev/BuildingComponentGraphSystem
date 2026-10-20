<template>
  <div class="video-button-container">
    <!-- 视频按钮 -->
    <button @click="showVideoModal" class="language-and-video-button">
      🎥
    </button>

    <!-- 使用 Teleport 将视频弹窗渲染到 body 中 -->
    <Teleport to="body">
      <div v-if="showVideo" class="video-modal" @click="hideVideoModal">
        <div class="video-modal-content" @click.stop>
          <div class="video-modal-header">
            <h3 class="video-title">{{ currentLanguage === 'zh' ?
              currentVideoIndex === 0 ? '第一步：创建房间' :
              currentVideoIndex === 1 ? '第二步：房间参数调节' :
              currentVideoIndex === 2 ? '第三步：预测结果' :
              '第四步：方案优化与导出'
              : currentVideoIndex === 0 ? 'Step 1: Create Room' :
              currentVideoIndex === 1 ? 'Step 2: Adjust Room Parameters' :
              currentVideoIndex === 2 ? 'Step 3: Prediction Results' :
              'Step 4: Optimization & Export' }} ({{ currentVideoIndex + 1 }}/{{ totalVideos }})</h3>
            <button @click="hideVideoModal" class="close-button">×</button>
          </div>
          <div class="video-container">
            <!-- 左箭头按钮 -->
            <button
              v-if="currentVideoIndex > 0"
              @click="previousVideo"
              class="video-nav-button prev-button"
              :title="currentLanguage === 'zh' ? '上一个视频' : 'Previous Video'"
            >
              <span class="nav-arrow">‹</span>
              <span class="nav-text">{{ currentLanguage === 'zh' ? '上一步' : 'Previous' }}</span>
            </button>

            <video
              ref="videoRef"
              :src="videoSrc"
              controls
              autoplay
              class="tutorial-video"
              @loadstart="onVideoLoadStart"
              @error="onVideoError"
            >
              {{ currentLanguage === 'zh' ? '您的浏览器不支持视频播放' : 'Your browser does not support video playback' }}
            </video>

            <!-- 右箭头按钮 -->
            <button
              v-if="currentVideoIndex < totalVideos - 1"
              @click="nextVideo"
              class="video-nav-button next-button"
              :title="currentLanguage === 'zh' ? '下一个视频' : 'Next Video'"
            >
              <span class="nav-text">{{ currentLanguage === 'zh' ? '下一步' : 'Next' }}</span>
              <span class="nav-arrow">›</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';

// 定义props接收语言信息和默认显示状态
const props = defineProps<{
  currentLanguage: string;
  defaultShow?: boolean;
}>();

// 添加视频相关的响应式变量
const showVideo = ref(props.defaultShow || false);  // 使用props控制默认状态
const videoRef = ref<HTMLVideoElement | null>(null);
const videoSrc = ref('/videos/page1.mp4');
const currentVideoIndex = ref(0);
const totalVideos = ref(4);
const videoList = ref([
  '/videos/page1.mp4',
  '/videos/page2.mp4',
  '/videos/page3.mp4',
  '/videos/page4.mp4'
]);

// 显示视频弹窗
const showVideoModal = () => {
  showVideo.value = true;
};

// 隐藏视频弹窗
const hideVideoModal = () => {
  showVideo.value = false;
};

// 切换到下一个视频
const nextVideo = () => {
  if (currentVideoIndex.value < totalVideos.value - 1) {
    currentVideoIndex.value++;
    videoSrc.value = videoList.value[currentVideoIndex.value];
  }
};

// 切换到上一个视频
const previousVideo = () => {
  if (currentVideoIndex.value > 0) {
    currentVideoIndex.value--;
    videoSrc.value = videoList.value[currentVideoIndex.value];
  }
};

// 视频加载开始
const onVideoLoadStart = () => {
  console.log('视频开始加载:', videoSrc.value);
};

// 视频加载错误
const onVideoError = () => {
  console.error('视频加载失败:', videoSrc.value);
};
</script>

<style scoped>
/* 视频按钮容器样式 */
.video-button-container {
  position: relative;
  z-index: 99998;
}

/* 视频按钮样式 */
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
}

.language-and-video-button:hover {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}
</style>

<style>
/* 视频弹窗样式 - 使用 Teleport 后不需要 scoped，直接渲染到 body */
.video-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 99999;
}

.video-modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  max-width: 80%;
  max-height: 85%;
  min-width: 600px;
  min-height: 400px;
  overflow: auto;
  z-index: 100000;
  position: relative;
}

.video-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.video-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
}

.close-button {
  background-color: transparent;
  border: none;
  color: #333;
  font-size: 28px;
  cursor: pointer;
  transition: color 0.3s;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #ff3b30;
}

.video-container {
  position: relative;
  width: 100%;
  height: 450px;
}

.tutorial-video {
  width: 100%;
  height: 100%;
  border-radius: 6px;
}

/* 视频导航按钮样式 */
.video-nav-button {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  border: none;
  min-width: 80px;
  height: 40px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.3s ease;
  z-index: 100001;
  padding: 0 12px;
  backdrop-filter: blur(4px);
}

.video-nav-button:hover {
  background-color: rgba(0, 0, 0, 0.9);
  transform: translateY(-50%) scale(1.05);
}

.nav-arrow {
  font-size: 18px;
  font-weight: bold;
}

.nav-text {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

.prev-button {
  left: 15px;
}

.next-button {
  right: 15px;
}

/* 中等屏幕（平板）响应式样式 */
@media (max-width: 1024px) {
  .video-modal-content {
    max-width: 90%;
    min-width: 400px;
    min-height: 300px;
  }

  .video-container {
    height: 350px;
  }

  .video-nav-button {
    min-width: 70px;
    height: 36px;
    font-size: 13px;
    padding: 0 10px;
  }

  .nav-arrow {
    font-size: 16px;
  }

  .nav-text {
    font-size: 11px;
  }
}

/* 移动端响应式样式 */
@media (max-width: 768px) {
  .video-modal-content {
    max-width: 95%;
    min-width: 280px;
    min-height: 200px;
    padding: 15px;
  }

  .video-container {
    height: 200px;
  }

  .video-title {
    font-size: 16px;
  }

  .close-button {
    font-size: 24px;
    width: 32px;
    height: 32px;
  }

  .video-nav-button {
    min-width: 60px;
    height: 32px;
    font-size: 12px;
    padding: 0 8px;
  }

  .nav-arrow {
    font-size: 14px;
  }

  .nav-text {
    font-size: 10px;
  }

  .prev-button {
    left: 10px;
  }

  .next-button {
    right: 10px;
  }
}
</style>
