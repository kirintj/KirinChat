<script setup lang="ts">
import { inject, ref, computed, onMounted } from "vue"
import { useRouter, useRoute } from "vue-router"
import { HMessage, HIcon, HDrawer, HStatusbar, HTitlebar, HBottomTab } from '@/components/ui'
import { useAgentCardStore } from "../store/agent_card"
import { useUserStore } from "../store/user"
import { logoutAPI, getUserInfoAPI } from "../apis/auth"
import {
  allMenuItems,
  coreTabs,
  secondaryItems,
  getTitleByRoute,
} from "../composables/useNavigation"

/* ---- inject mobile flag from HAppShell ---- */
const isMobile = inject<import('vue').Ref<boolean>>('isMobile', ref(false))

/* ---- stores & router ---- */
const agentCardStore = useAgentCardStore()
const userStore = useUserStore()
const route = useRoute()
const router = useRouter()

/* ---- sidebar state (desktop) ---- */
const sidebarCollapsed = ref(false)
const toggleSidebar = () => { sidebarCollapsed.value = !sidebarCollapsed.value }

/* ---- user dropdown (desktop) ---- */
const showUserMenu = ref(false)
const toggleUserMenu = () => { showUserMenu.value = !showUserMenu.value }

/* ---- desktop menu helpers ---- */
const goCurrent = (key: string) => {
  const item = allMenuItems.find(m => m.key === key)
  if (item) router.push(item.route)
}

/* ---- mobile bottom tab ---- */
const bottomTabItems = coreTabs.map(t => ({ key: t.key, label: t.label, icon: t.icon }))
const currentTabKey = computed(() => {
  const match = coreTabs.find(t => route.path.startsWith(t.route))
  return match?.key ?? 'workspace'
})
const onTabChange = (key: string) => {
  const item = coreTabs.find(t => t.key === key)
  if (item) router.push(item.route)
}

/* ---- mobile "more" drawer ---- */
const showMoreDrawer = ref(false)

/* ---- mobile titlebar ---- */
const mobileTitle = computed(() => getTitleByRoute(route.path))
const mobileTitleVariant = computed<'big' | 'normal'>(() =>
  route.path === '/homepage' ? 'big' : 'normal'
)

/* ---- active menu key (by route path) ---- */
const current = computed(() => {
  const match = allMenuItems.find(m => route.path.startsWith(m.route))
  return match?.key || ''
})

/* ---- user dropdown commands ---- */
const handleUserCommand = async (command: string) => {
  switch (command) {
    case 'profile': router.push('/profile'); break
    case 'settings': router.push('/configuration'); break
    case 'logout': await handleLogout(); break
  }
}

const handleLogout = async () => {
  try { await logoutAPI() } catch (e) { console.error('调用登出接口失败:', e) }
  userStore.logout()
  HMessage.success('已退出登录')
  router.push('/login')
}

const handleAvatarError = (event: Event) => {
  const target = event.target as HTMLImageElement
  if (target) target.src = '/user.svg'
}

const godefault = () => {
  agentCardStore.clear()
  router.push("/")
}

/* ---- init user ---- */
onMounted(async () => {
  userStore.initUserState()
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
})
</script>

<template>
  <div class="ai-body" :class="{ 'ai-body--mobile': isMobile }">
    <!-- ==================== DESKTOP ==================== -->
    <template v-if="!isMobile">
      <div class="ai-desktop">
        <!-- sidebar -->
        <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
          <!-- brand area -->
          <div class="sidebar-brand" @click="godefault">
            <span class="sidebar-brand__name">KirinChat</span>
          </div>

          <div class="sidebar-divider" />

          <!-- menu -->
          <div class="sidebar-menu">
            <div
              v-for="item in allMenuItems"
              :key="item.key"
              class="menu-item"
              :class="{ active: current === item.key }"
              @click="goCurrent(item.key)"
              :title="sidebarCollapsed ? item.label : ''"
            >
              <div class="menu-icon">
                <HIcon :svg="item.icon" :size="18" />
              </div>
              <span v-if="!sidebarCollapsed" class="menu-text">{{ item.label }}</span>
            </div>
          </div>

          <div class="sidebar-divider" />

          <!-- user area -->
          <div class="sidebar-user">
            <div class="user-dropdown" @click="toggleUserMenu">
              <div class="user-avatar-wrapper">
                <img
                  :src="userStore.userInfo?.avatar || '/user.svg'"
                  alt="用户头像"
                  @error="handleAvatarError"
                  referrerpolicy="no-referrer"
                />
              </div>
              <span v-if="!sidebarCollapsed" class="sidebar-user__name">
                {{ userStore.userInfo?.name || '用户' }}
              </span>
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

          <!-- collapse toggle -->
          <div class="sidebar-toggle" @click="toggleSidebar">
            <span class="toggle-icon">{{ sidebarCollapsed ? '›' : '‹' }}</span>
          </div>
        </div>

        <!-- content -->
        <div class="content">
          <router-view />
        </div>
      </div>
    </template>

    <!-- ==================== MOBILE ==================== -->
    <template v-else>
      <div class="ai-mobile">
        <HStatusbar theme="light" />
        <HTitlebar
          :variant="mobileTitleVariant"
          :title="mobileTitle"
        >
          <template #actions>
            <div class="more-btn" @click="showMoreDrawer = true">
              <HIcon name="Menu" :size="22" />
            </div>
          </template>
        </HTitlebar>

        <div class="mobile-content">
          <router-view />
        </div>

        <HBottomTab
          variant="4"
          :items="bottomTabItems"
          :active-key="currentTabKey"
          @update:active-key="onTabChange"
        />
      </div>
    </template>

    <!-- more drawer (outside ai-mobile so it teleports correctly) -->
    <HDrawer v-model="showMoreDrawer" title="更多" direction="right" size="85vw">
      <div class="more-grid">
        <div
          v-for="item in secondaryItems"
          :key="item.key"
          class="more-grid__card"
          @click="goCurrent(item.key); showMoreDrawer = false"
        >
          <HIcon :svg="item.icon" :size="28" />
          <span class="more-grid__label">{{ item.label }}</span>
        </div>
      </div>
    </HDrawer>
  </div>
</template>

<style lang="scss" scoped>
.ai-body {
  overflow: hidden;
  width: 100%;
  height: 100%;
}

/* ==================== DESKTOP ==================== */
.ai-desktop {
  display: flex;
  height: 100vh;
  padding: 16px;
  gap: 16px;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eeff 50%, #f5f0ff 100%);
  box-sizing: border-box;

  .sidebar {
    width: 200px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.4);
    backdrop-filter: blur(80px);
    -webkit-backdrop-filter: blur(80px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0, 0, 0, 0.04);
    padding: 12px 10px;
    transition: width 0.2s ease;

    &.collapsed {
      width: 64px;
    }

    .sidebar-brand {
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 8px;
      cursor: pointer;

      &__name {
        font-size: var(--harmony-font-size-body-l);
        font-weight: 700;
        color: var(--harmony-font-primary);
        letter-spacing: -0.02em;
      }
    }

    .sidebar-divider {
      height: 1px;
      margin: 4px 12px;
      background: var(--harmony-comp-divider);
    }

    .sidebar-menu {
      flex: 1;
      overflow-y: auto;
      padding: 4px 0;

      .menu-item {
        display: flex;
        align-items: center;
        gap: 8px;
        padding: 8px 14px;
        border-radius: 14px;
        cursor: pointer;
        margin-bottom: 1px;
        color: var(--harmony-font-secondary);
        font-size: var(--harmony-font-size-body-m);
        transition: all 0.15s ease;

        &:hover {
          background: var(--harmony-interactive-hover);
          color: var(--harmony-font-primary);
        }

        &.active {
          background: rgba(10, 89, 247, 0.098);
          color: var(--harmony-brand);
          font-weight: 500;
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

    .sidebar-user {
      padding: 4px;

      .user-dropdown {
        position: relative;
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 6px 10px;
        border-radius: 14px;
        cursor: pointer;
        transition: background 0.15s ease;

        &:hover {
          background: var(--harmony-interactive-hover);
        }
      }

      .user-avatar-wrapper img {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
      }

      .sidebar-user__name {
        font-size: var(--harmony-font-size-body-s);
        color: var(--harmony-font-primary);
        font-weight: 500;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
    }

    .sidebar-toggle {
      text-align: center;
      padding: 8px 0;
      cursor: pointer;

      .toggle-icon {
        display: inline-block;
        width: 24px;
        height: 24px;
        line-height: 24px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 8px;
        font-size: var(--harmony-font-size-body-s);
        color: var(--harmony-font-secondary);
      }
    }
  }

  .content {
    flex: 1;
    overflow-y: auto;
    border-radius: 28px;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(40px);
    -webkit-backdrop-filter: blur(40px);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.04);
  }
}

/* ==================== MOBILE ==================== */
.ai-mobile {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background: var(--harmony-comp-background-primary);

  .more-btn {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: pointer;
    color: var(--harmony-font-primary);
    transition: background 0.15s ease;

    &:active {
      background: var(--harmony-interactive-pressed);
    }
  }

  .mobile-content {
    flex: 1;
    overflow-y: auto;
    padding-bottom: 100px; /* room for bottom tab */
  }
}

/* ==================== MORE DRAWER GRID ==================== */
.more-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;

  &__card {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 20px 12px;
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.45);
    backdrop-filter: blur(12px);
    cursor: pointer;
    transition: background 0.15s ease;

    &:active {
      background: var(--harmony-interactive-pressed);
    }
  }

  &__label {
    font-size: var(--harmony-font-size-body-s);
    color: var(--harmony-font-primary);
    font-weight: 500;
  }
}

/* ==================== USER DROPDOWN (shared) ==================== */
.user-dropdown {
  position: relative;
}

.user-dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
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
</style>
