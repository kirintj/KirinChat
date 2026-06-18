<script setup lang="ts">
import { onMounted, ref, watch, computed } from "vue"
import { useRouter } from "vue-router"
import { useRoute } from "vue-router"
import { HMessage } from '@/components/ui'
import workspaceIcon from '../assets/workspace.svg'
import applicationCenterIcon from '../assets/application-center.svg'
import exploreIcon from '../assets/explore.svg'
import dialogIcon from '../assets/dialog.svg'
import robotIcon from '../assets/robot.svg'
import pluginIcon from '../assets/plugin.svg'
import knowledgeIcon from '../assets/knowledge.svg'
import modelIcon from '../assets/model.svg'
import mcpIcon from '../assets/mcp.svg'
import skillIcon from '../assets/skill.svg'
import dashboardIcon from '../assets/dashboard.svg'
import { useAgentCardStore } from "../store/agent_card"
import { useUserStore } from "../store/user"
import { getAgentsAPI } from "../apis/agent"
import { logoutAPI, getUserInfoAPI } from "../apis/auth"
import { Agent } from "../type"

const agentCardStore = useAgentCardStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()
const itemName = ref("麒麟智聊平台")
const showAppCenterMenu = ref(false)
let appCenterHoverTimer: any = null

const sidebarCollapsed = ref(false)

const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

const menuItems = [
  { index: 'workspace', label: '工作台', icon: workspaceIcon },
  { index: 'homepage', label: '探索', icon: exploreIcon },
  { index: 'conversation', label: '会话', icon: dialogIcon },
  { index: 'agent', label: '智能体', icon: robotIcon },
  { index: 'mcp-server', label: 'MCP', icon: mcpIcon },
  { index: 'knowledge', label: '知识库', icon: knowledgeIcon },
  { index: 'tool', label: '工具', icon: pluginIcon },
  { index: 'agent-skill', label: 'Skill', icon: skillIcon },
  { index: 'model', label: '模型', icon: modelIcon },
  { index: 'dashboard', label: '数据看板', icon: dashboardIcon },
]

const openAppCenterMenu = () => {
  if (appCenterHoverTimer) clearTimeout(appCenterHoverTimer)
  showAppCenterMenu.value = true
}

const closeAppCenterMenu = () => {
  if (appCenterHoverTimer) clearTimeout(appCenterHoverTimer)
  appCenterHoverTimer = setTimeout(() => {
    showAppCenterMenu.value = false
  }, 120)
}

const goWorkspaceTop = () => {
  router.push('/workspace')
}

const appCenterColumns = ref([
  [
    { label: '会话', icon: dialogIcon, route: '/conversation' },
    { label: '工作台', icon: workspaceIcon, route: '/workspace' }
  ],
  [
    { label: '智能体', icon: robotIcon, route: '/agent' },
    { label: '工具', icon: pluginIcon, route: '/tool' }
  ],
  [
    { label: '知识库', icon: knowledgeIcon, route: '/knowledge' },
    { label: '模型', icon: modelIcon, route: '/model' }
  ],
  [
    { label: 'MCP', icon: mcpIcon, route: '/mcp-server' },
    { label: 'Skill', icon: skillIcon, route: '/agent-skill' }
  ]
])
const current = ref(route.meta.current)
const cardList = ref<Agent[]>([])

// 顶栏按钮激活态
const isWorkspaceActive = computed(() => route.path.startsWith('/workspace'))
const isAppCenterActive = computed(() => route.path.startsWith('/homepage'))

// 初始化用户状态
onMounted(async () => {
  userStore.initUserState()
  
  // 如果已登录但没有头像，则尝试获取用户信息
  if (userStore.isLoggedIn && userStore.userInfo && !userStore.userInfo.avatar) {
    try {
      const response = await getUserInfoAPI(userStore.userInfo.id)
      if (response.data.status_code === 200 && response.data.data) {
        const userData = response.data.data
        userStore.updateUserInfo({
          avatar: userData.user_avatar || userData.avatar || '/src/assets/user.svg',
          description: userData.user_description || userData.description
        })
      }
    } catch (error) {
      console.error('初始化时获取用户信息失败:', error)
    }
  }
  
  updateList()
})

const godefault = () => {
  agentCardStore.clear()
  router.push("/")
}
  
const updateList = async () => {
  try {
    const response = await getAgentsAPI()
    cardList.value = response.data.data
  } catch (error) {
    console.error('获取智能体列表失败:', error)
  }
}

const goCurrent = (item: string) => {
  const routes: Record<string, string> = {
    "homepage": "/homepage",
    "conversation": "/conversation",
    "agent": "/agent",
    "mcp-server": "/mcp-server",
    "mcp-chat": "/mcp-server/chat",
    "knowledge": "/knowledge",
    "tool": "/tool",
    "agent-skill": "/agent-skill",
    "model": "/model",
    "workspace": "/workspace",
    "dashboard": "/dashboard"
  }

  router.push(routes[item] || "/")
}

// 用户下拉菜单命令处理
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile':
      router.push('/profile')
      break
    case 'settings':
      router.push('/configuration')
      break
    case 'logout':
      await handleLogout()
      break
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    await logoutAPI()
  } catch (error) {
    console.error('调用登出接口失败:', error)
  }
  userStore.logout()
  HMessage.success('已退出登录')
  router.push('/login')
}

// 头像加载错误处理
const handleAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) {
    target.src = '/src/assets/user.svg'
  }
}

watch(
  route,
  (val) => {
    current.value = route.meta.current
  },
  {
    immediate: true
  }
)
</script>

<template>
  <div class="ai-body">
    <div class="ai-nav">
      <div class="left">
  <div class="brand-name" @click="godefault">KirinChat</div>
</div>
      <div class="right">
        <button class="new-chat-btn" @click="goCurrent('conversation')">
          新建会话
        </button>
        <div class="user-info">
          <div class="user-dropdown" @click="toggleUserMenu">
            <div class="user-avatar-wrapper">
              <div class="user-avatar">
                <img
                  :src="userStore.userInfo?.avatar || '/src/assets/user.svg'"
                  alt="用户头像"
                  @error="handleAvatarError"
                  referrerpolicy="no-referrer"
                />
              </div>
            </div>
            <div v-if="showUserMenu" class="user-dropdown-menu">
              <div class="user-dropdown-item" @click="handleUserCommand('profile')">
                <span>个人资料</span>
              </div>
              <div class="user-dropdown-item user-dropdown-item--danger" @click="handleUserCommand('logout')">
                <span>退出登录</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="ai-main">
      <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
        <div class="sidebar-menu">
          <div
            v-for="item in menuItems"
            :key="item.index"
            class="menu-item"
            :class="{ active: current === item.index }"
            @click="goCurrent(item.index)"
            :title="sidebarCollapsed ? item.label : ''"
          >
            <div class="menu-icon">
              <img :src="item.icon" width="18px" height="18px" />
            </div>
            <span v-if="!sidebarCollapsed" class="menu-text">{{ item.label }}</span>
          </div>
        </div>
        <div class="sidebar-toggle" @click="toggleSidebar">
          <span class="toggle-icon">{{ sidebarCollapsed ? '›' : '‹' }}</span>
        </div>
      </div>
      <div class="content">
        <router-view></router-view>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ai-body {
@import url('https://fonts.googleapis.com/css2?family=ZCOOL+KuaiLe&family=Zhi+Mang+Xing&family=Ma+Shan+Zheng&display=swap');
}
.ai-body {
  overflow: hidden;
  
  .ai-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 52px;
    background: var(--color-bg);
    padding: 0 var(--spacing-xl);
    border-bottom: 1px solid var(--color-border);
    position: relative;
    z-index: 3000;

    .left {
      display: flex;
      align-items: center;
      gap: var(--spacing-md);

      .brand-name {
        font-size: 15px;
        font-weight: 600;
        color: var(--color-text-primary);
        cursor: pointer;
      }
    }

    .right {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);

      .new-chat-btn {
        background: var(--color-primary);
        color: var(--color-bg);
        border: none;
        padding: 7px 18px;
        border-radius: var(--radius-md);
        font-size: 13px;
        font-weight: 500;
        cursor: pointer;
        transition: background-color 0.2s;

        &:hover {
          background: var(--color-primary-hover);
        }
      }

      .user-info {
        .user-avatar-wrapper {
          cursor: pointer;

          .user-avatar img {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            object-fit: cover;
          }
        }
      }
    }
  }
  
  .ai-main {
    display: flex;
    height: calc(100vh - 52px);
    background: var(--color-bg-secondary);

    .sidebar {
      width: 200px;
      background: var(--color-bg-tertiary);
      border-right: 1px solid var(--color-border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: width 0.2s ease;

      &.collapsed {
        width: 64px;
      }

      .sidebar-menu {
        flex: 1;
        padding: var(--spacing-md) var(--spacing-xs);
        overflow-y: auto;

        .menu-item {
          display: flex;
          align-items: center;
          gap: var(--spacing-sm);
          padding: 10px 14px;
          border-radius: var(--radius-md);
          cursor: pointer;
          margin-bottom: 4px;
          color: var(--color-text-secondary);
          font-size: 13px;
          transition: all 0.2s ease;

          &:hover {
            background: var(--color-bg);
            color: var(--color-text-primary);
          }

          &.active {
            background: var(--color-bg);
            color: var(--color-text-primary);
            font-weight: 500;
            box-shadow: var(--shadow-card);
          }

          .menu-icon {
            width: 18px;
            height: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
          }

          .menu-text {
            white-space: nowrap;
            overflow: hidden;
          }
        }
      }

      .sidebar-toggle {
        text-align: center;
        padding: var(--spacing-sm) 0;
        border-top: 1px solid var(--color-border);
        cursor: pointer;

        .toggle-icon {
          display: inline-block;
          width: 24px;
          height: 24px;
          line-height: 24px;
          background: var(--color-bg-secondary);
          border-radius: var(--radius-sm);
          font-size: 12px;
          color: var(--color-text-secondary);
        }
      }
    }

    .content {
      flex: 1;
      overflow-y: auto;
      padding: var(--spacing-xl);
    }
  }
}

.user-dropdown {
  position: relative;
  cursor: pointer;

  .user-dropdown-menu {
    position: absolute;
    top: 100%;
    right: 0;
    margin-top: 8px;
    min-width: 140px;
    background: var(--color-bg-secondary);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    z-index: var(--z-dropdown);
    overflow: hidden;
    animation: fadeSlideIn var(--duration-fast) var(--easing);
  }

  .user-dropdown-item {
    padding: 10px 16px;
    font-size: var(--font-size-base);
    color: var(--color-text-primary);
    cursor: pointer;
    transition: background var(--duration-fast) var(--easing);

    &:hover {
      background: var(--color-bg-tertiary);
    }

    &--danger {
      color: var(--color-danger);
    }
  }
}

@keyframes fadeSlideIn {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
