import { createRouter, createWebHistory } from 'vue-router'
import AppShell  from '@/views/AppShell.vue'
import AskView   from '@/views/AskView.vue'
import AgentView from '@/views/AgentView.vue'
import RoastView from '@/views/RoastView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: AppShell,
      children: [
        { path: '',      redirect: '/ask' },
        { path: 'ask',   name: 'ask',   component: AskView   },
        { path: 'agent', name: 'agent', component: AgentView },
        { path: 'roast', name: 'roast', component: RoastView },
      ],
    },
  ],
})

export default router
