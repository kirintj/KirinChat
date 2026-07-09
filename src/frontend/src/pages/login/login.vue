<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage, HButton, HInput } from '@/components/ui'
import { loginAPI, getUserInfoAPI } from '../../apis/auth'
import { useUserStore } from '../../store/user'

const router = useRouter()
const userStore = useUserStore()

const loginForm = reactive({
  username: '',
  password: ''
})

const loading = ref(false)

const handleLogin = async () => {
  if (!loginForm.username || !loginForm.password) {
    HMessage.warning('请输入用户名和密码')
    return
  }

  try {
    loading.value = true
    const response = await loginAPI(loginForm)
    
    // response.data结构可能是{status_code: number, data: {...}}
    const responseData = response.data
    if (responseData.status_code === 200) {
      HMessage.success('登录成功')
      
      // 使用store管理用户状态
      const userData = responseData.data || {}
      if (userData.access_token && userData.user_id) {
        // 先保存基础用户信息
        userStore.setUserInfo(userData.access_token, {
          id: userData.user_id,
          username: loginForm.username
        })
        
        // 立即获取完整的用户信息（包括头像等）
        try {
          const userInfoResponse = await getUserInfoAPI(userData.user_id)
          const userInfoData = userInfoResponse.data
          if (userInfoData.status_code === 200) {
            const completeUserData = userInfoData.data || {}
            // 更新用户信息，包含头像
            userStore.updateUserInfo({
              avatar: completeUserData.user_avatar || completeUserData.avatar,
              description: completeUserData.user_description || completeUserData.description
            })
          }
        } catch (error) {
          console.error('获取用户详细信息失败:', error)
        }
      }
      
      // 跳转到主页
      router.push('/')
    } else {
      HMessage.error(responseData.status_message || '登录失败')
    }
  } catch (error: any) {
    console.error('登录错误:', error)
    if (error.response?.data?.status_message) {
      HMessage.error(error.response.data.status_message)
    } else if (error.response?.data?.detail) {
      HMessage.error(error.response.data.detail)
    } else if (error.response?.data?.message) {
      HMessage.error(error.response.data.message)
    } else {
      HMessage.error('登录失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="auth-page">
    <div class="card">
      <div class="header">
        <div class="logo"><span class="logo__text">KirinChat</span></div>
        <p class="subtitle">更智能、更多元的大模型应用开发平台</p>
      </div>

      <div class="field">
        <label class="field__label">账号</label>
        <HInput v-model="loginForm.username" placeholder="请输入账号" size="large" class="field__input" @keyup.enter="handleLogin" />
      </div>

      <div class="field">
        <label class="field__label">密码</label>
        <HInput v-model="loginForm.password" type="password" placeholder="请输入密码" size="large" class="field__input" :show-password="true" @keyup.enter="handleLogin" />
      </div>

      <div class="actions">
        <span class="switch-link">没有账号？<a href="#" @click.prevent="goToRegister">注册</a></span>
      </div>

      <button class="primary-btn" :disabled="loading" @click="handleLogin">
        {{ loading ? '登录中…' : '登录' }}
      </button>

      <div class="footer">
        <span class="version-badge">v2.5.0</span>
        <div class="footer-icons">
          <a href="https://github.com/kirintj/KirinChat" target="_blank" title="GitHub">
            <img src="../../assets/github.png" alt="GitHub" />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* 极简规则：
   - auth-page：全屏居中（背景色用全局 token）
   - card：卡片容器（宽度/圆角/阴影/内边距）
   - header/logo/subtitle：头部排版
   - .field / .field__label：字段间距 + 标签样式
   - .primary-btn：主按钮（因为登录/注册页按钮就是主色大按钮）
   - .actions / .switch-link / .footer：辅助文字与链接
   - 输入框的边框/背景/hover/focus 全部由 HInput 组件自身负责，这里不二次覆盖
*/
$brand-shadow: var(--harmony-comp-emphasize-secondary);

.auth-page {
  width: 100%;
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background: var(--harmony-background-secondary);
  font-family: var(--harmony-font-family);
}

.card {
  width: 100%;
  max-width: 380px;
  background: var(--harmony-background-primary);
  border-radius: var(--harmony-corner-radius-level10);
  box-shadow: var(--harmony-shadow-md);
  padding: 40px 32px 24px;
}

.header { text-align: center; margin-bottom: 28px; }
.header .logo { margin-bottom: 12px; }

.header .logo__text {
  display: inline-block;
  background: linear-gradient(135deg, var(--harmony-brand), var(--harmony-comp-emphasize-secondary) 160%, var(--harmony-brand));
  color: #fff;
  padding: 10px 22px;
  border-radius: var(--harmony-corner-radius-level4);
  font-size: var(--harmony-font-size-title-s);
  font-weight: 700;
  letter-spacing: 2px;
  box-shadow: 0 4px 16px $brand-shadow;
}

.header .subtitle {
  color: var(--harmony-font-secondary);
  font-size: var(--harmony-font-size-body-l);
  line-height: 1.6;
  margin: 0;
}

/* 字段组：只控制垂直间距与标签样式，输入框本体交由 HInput */
.field { margin-bottom: 16px; }

.field__label {
  display: block;
  margin-bottom: 6px;
  font-size: var(--harmony-font-size-body-m);
  font-weight: 600;
  color: var(--harmony-font-primary);
}

.actions {
  display: flex;
  justify-content: flex-end;
  margin: 4px 0 20px;
}

.switch-link {
  font-size: var(--harmony-font-size-subtitle-m);
  color: var(--harmony-font-secondary);
}

.switch-link a {
  color: var(--harmony-brand);
  margin-left: 6px;
  font-weight: 500;
  text-decoration: none;

  &:hover { color: var(--harmony-interactive-pressed); text-decoration: underline; }
}

.primary-btn {
  width: 100%;
  height: 48px;
  border: none;
  border-radius: var(--harmony-corner-radius-level5);
  background: linear-gradient(135deg, var(--harmony-brand), var(--harmony-interactive-pressed));
  color: #fff;
  font-size: var(--harmony-font-size-subtitle-l);
  font-weight: 600;
  letter-spacing: 1px;
  cursor: pointer;
  transition: transform var(--harmony-duration-normal) var(--harmony-motion-standard),
              box-shadow var(--harmony-duration-normal) var(--harmony-motion-standard);

  &:hover  { transform: translateY(-1px); box-shadow: 0 8px 24px $brand-shadow; }
  &:active { transform: translateY(0); }
  &:disabled { opacity: 0.7; cursor: not-allowed; }
}

.footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 14px;
  border-top: 1px solid var(--harmony-comp-divider);
  font-size: var(--harmony-font-size-subtitle-s);
  color: var(--harmony-font-tertiary);
}

.footer .version-badge {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: var(--harmony-corner-radius-level18);
  background: var(--harmony-comp-emphasize-tertiary);
  color: var(--harmony-brand);
  font-weight: 600;
}

.footer .footer-icons {
  display: flex;
  gap: 10px;

  a {
    width: 26px;
    height: 26px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--harmony-comp-background-secondary);
    border: 1px solid var(--harmony-comp-divider);
    border-radius: var(--harmony-corner-radius-level4);
    overflow: hidden;

    &:hover {
      box-shadow: 0 6px 16px $brand-shadow;
      border-color: color-mix(in srgb, var(--harmony-brand) 40%, transparent);
    }

    img { width: 16px; height: 16px; object-fit: contain; }
  }
}
</style>