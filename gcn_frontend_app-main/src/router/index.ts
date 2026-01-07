import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SecondView from '../views/SecondView.vue'
import ThirdView from '../views/ThirdView.vue'
import OptView from '../views/OptView.vue'

// 扩展ImportMeta接口
declare global {
  interface ImportMeta {
    env: Record<string, string>;
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/second',
      name: 'second',
      component: SecondView
    },
    {
      path: '/third',
      name: 'third',
      component: ThirdView
    },
    {
      path: '/opt',
      name: 'opt',
      component: OptView
    }
  ],
})

export default router
