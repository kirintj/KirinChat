<script setup lang="ts">
import { onMounted, ref, watch, computed } from "vue"
import { useRouter } from "vue-router"
import { useRoute } from "vue-router"
import { HMessage, HIcon } from '@/components/ui'
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
  { index: 'workspace', label: '工作台', icon: 'workspace' },
  { index: 'homepage', label: '探索', icon: 'explore' },
  { index: 'conversation', label: '会话', icon: 'dialog' },
  { index: 'agent', label: '智能体', icon: 'robot' },
  { index: 'mcp-server', label: 'MCP', icon: 'mcp' },
  { index: 'knowledge', label: '知识库', icon: 'knowledge' },
  { index: 'tool', label: '工具', icon: 'plugin' },
  { index: 'agent-skill', label: 'Skill', icon: 'skill' },
  { index: 'interview', label: '面试', icon: 'skill' },
  { index: 'model', label: '模型', icon: 'model' },
  { index: 'dashboard', label: '数据看板', icon: 'dashboard' },
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
    { label: '会话', icon: 'dialog', route: '/conversation' },
    { label: '工作台', icon: 'workspace', route: '/workspace' }
  ],
  [
    { label: '智能体', icon: 'robot', route: '/agent' },
    { label: '工具', icon: 'plugin', route: '/tool' }
  ],
  [
    { label: '知识库', icon: 'knowledge', route: '/knowledge' },
    { label: '模型', icon: 'model', route: '/model' }
  ],
  [
    { label: 'MCP', icon: 'mcp', route: '/mcp-server' },
    { label: 'Skill', icon: 'skill', route: '/agent-skill' }
  ]
])
const current = ref(route.meta.current)
const cardList = ref<Agent[]>([])
const agentsError = ref('')
const agentsRetryable = ref(false)

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
          avatar: userData.user_avatar || userData.avatar || '/user.svg',
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
  agentsError.value = ''
  agentsRetryable.value = false
  try {
    const response = await getAgentsAPI()
    cardList.value = response.data.data
  } catch (error: any) {
    const msg = error?.friendlyMessage || '获取智能体列表失败'
    console.error(msg, error)
    agentsError.value = msg
    agentsRetryable.value = error?.code === 'ECONNABORTED' || !error?.response
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
    "interview": "/interview",
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
    target.src = '/user.svg'
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
        <div class="user-info">
          <div class="user-dropdown" @click="toggleUserMenu">
            <div class="user-avatar-wrapper">
              <div class="user-avatar">
                <img
                  :src="userStore.userInfo?.avatar || '/user.svg'"
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
              <HIcon :svg="item.icon" :size="18" />
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
    background: var(--harmony-comp-background-primary);
    padding: 0 var(--harmony-padding-level12);
    border-bottom: 1px solid var(--harmony-comp-divider);
    position: relative;
    z-index: var(--z-dropdown);

    .left {
      display: flex;
      align-items: center;
      gap: var(--harmony-padding-level8);

      .brand-name {
        font-size: var(--harmony-font-size-body-l);
        font-weight: 600;
        color: var(--harmony-font-primary);
        cursor: pointer;
      }
    }

    .right {
      display: flex;
      align-items: center;
      gap: var(--harmony-padding-level6);

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
    background: var(--harmony-comp-background-secondary);

    .sidebar {
      width: 200px;
      background: var(--harmony-comp-background-tertiary);
      border-right: 1px solid var(--harmony-comp-divider);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: width 0.2s ease;

      &.collapsed {
        width: 64px;
      }

      .sidebar-menu {
        flex: 1;
        padding: var(--harmony-padding-level8) var(--harmony-padding-level4);
        overflow-y: auto;

        .menu-item {
          display: flex;
          align-items: center;
          gap: var(--harmony-padding-level6);
          padding: 10px 14px;
          border-radius: var(--harmony-corner-radius-level6);
          cursor: pointer;
          margin-bottom: 4px;
          color: var(--harmony-font-secondary);
          font-size: var(--harmony-font-size-body-m);
          transition: all 0.2s ease;

          &:hover {
            background: var(--harmony-comp-background-primary);
            color: var(--harmony-font-primary);
          }

          &.active {
            background: var(--harmony-comp-background-primary);
            color: var(--harmony-font-primary);
            font-weight: 500;
            box-shadow: var(--harmony-shadow-card);
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
        padding: var(--harmony-padding-level6) 0;
        border-top: 1px solid var(--harmony-comp-divider);
        cursor: pointer;

        .toggle-icon {
          display: inline-block;
          width: 24px;
          height: 24px;
          line-height: 24px;
          background: var(--harmony-comp-background-secondary);
          border-radius: var(--harmony-corner-radius-level4);
          font-size: var(--harmony-font-size-body-s);
          color: var(--harmony-font-secondary);
        }
      }
    }

    .content {
      flex: 1;
      overflow-y: auto;
      padding: 0;
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
    background: var(--harmony-comp-background-secondary);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level6);
    box-shadow: var(--harmony-shadow-md);
    z-index: var(--z-dropdown);
    overflow: hidden;
    animation: harmony-slide-up var(--harmony-duration-fast) var(--harmony-motion-standard);
  }

  .user-dropdown-item {
    padding: 10px 16px;
    font-size: var(--harmony-font-size-body-m);
    color: var(--harmony-font-primary);
    cursor: pointer;
    transition: background var(--harmony-duration-fast) var(--harmony-motion-standard);

    &:hover {
      background: var(--harmony-comp-background-tertiary);
    }

    &--danger {
      color: var(--harmony-warning);
    }
  }
}


  to { opacity: 1; transform: translateY(0); }
}
</style>
