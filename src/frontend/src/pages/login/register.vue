<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { HMessage, HButton, HInput } from '@/components/ui'
import { registerAPI } from '../../apis/auth'
import type { RegisterForm } from '../../apis/auth'

const router = useRouter()

const registerForm = reactive<RegisterForm>({
  user_name: '',
  user_email: '',
  user_password: ''
})

const confirmPassword = ref('')
const loading = ref(false)

const validateForm = () => {
  if (!registerForm.user_name) {
    HMessage.warning('请输入用户名')
    return false
  }
  
  if (registerForm.user_name.length > 20) {
    HMessage.warning('用户名长度不应该超过20个字符')
    return false
  }
  
  if (!registerForm.user_password) {
    HMessage.warning('请输入密码')
    return false
  }
  
  if (registerForm.user_password.length < 6) {
    HMessage.warning('密码长度至少6个字符')
    return false
  }
  
  if (registerForm.user_password !== confirmPassword.value) {
    HMessage.warning('两次输入的密码不一致')
    return false
  }
  
  if (registerForm.user_email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(registerForm.user_email)) {
    HMessage.warning('请输入有效的邮箱地址')
    return false
  }
  
  return true
}

const handleRegister = async () => {
  if (!validateForm()) {
    return
  }

  try {
    loading.value = true
    const response = await registerAPI(registerForm)
    
    if (response.data.status_code === 200) {
      HMessage.success('注册成功，请登录')
      // 跳转到登录页面
      router.push('/login')
    } else {
      HMessage.error(response.data.status_message || '注册失败')
    }
  } catch (error: any) {
    console.error('注册错误:', error)
    if (error.response?.data?.detail) {
      HMessage.error(error.response.data.detail)
    } else {
      HMessage.error('注册失败，请检查网络连接')
    }
  } finally {
    loading.value = false
  }
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="auth-page">
    <div class="card">
      <div class="header">
        <div class="logo"><span class="logo__text">KirinChat</span></div>
        <p class="subtitle">创建您的账户，开始智能对话之旅</p>
      </div>

      <div class="field">
        <label class="field__label">用户名</label>
        <HInput v-model="registerForm.user_name" placeholder="请输入用户名（最多 20 个字符）" size="large" class="field__input" @keyup.enter="handleRegister" />
      </div>

      <div class="field">
        <label class="field__label">邮箱（可选）</label>
        <HInput v-model="registerForm.user_email" placeholder="请输入邮箱地址" size="large" class="field__input" @keyup.enter="handleRegister" />
      </div>

      <div class="field">
        <label class="field__label">密码</label>
        <HInput v-model="registerForm.user_password" type="password" placeholder="请输入密码（至少 6 个字符）" size="large" class="field__input" :show-password="true" @keyup.enter="handleRegister" />
      </div>

      <div class="field">
        <label class="field__label">确认密码</label>
        <HInput v-model="confirmPassword" type="password" placeholder="请再次输入密码" size="large" class="field__input" :show-password="true" @keyup.enter="handleRegister" />
      </div>

      <div class="actions">
        <span class="switch-link">已有账号？<a href="#" @click.prevent="goToLogin">登录</a></span>
      </div>

      <button class="primary-btn" :disabled="loading" @click="handleRegister">
        {{ loading ? '注册中…' : '注册' }}
      </button>

      <div class="footer">
        <span class="version-badge">v2.5.0</span>
        <div class="footer-icons">
          <a href="https://github.com/kirintj/KirinChat" target="_blank" title="GitHub">
            <img src="../../assets/github.png" alt="GitHub" />
          </a>
          <a href="https://uawlh9wstr9.feishu.cn/wiki/QOaLwMDtBiiduWk4YtAcavEsnne" target="_blank" title="帮助文档">
            <img src="../../assets/help.png" alt="帮助文档" />
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
/* 与 login.vue 一致的卡片布局。
   输入框样式完全交给 HInput 组件本身，页面只负责排版与主色按钮。 */
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
  max-width: 400px;
  background: var(--harmony-background-primary);
  border-radius: var(--harmony-corner-radius-level10);
  box-shadow: var(--harmony-shadow-md);
  padding: 32px 32px 24px;
}

.header { text-align: center; margin-bottom: 20px; }
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

/* 字段组：只做排版，不覆盖输入框自身样式 */
.field { margin-bottom: 12px; }

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
  margin: 4px 0 16px;
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
  margin-top: 20px;
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