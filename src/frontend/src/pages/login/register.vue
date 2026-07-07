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
  <div class="register-container">
    <!-- 左侧3D图形区域 -->
    <div class="left-section">
      <div class="graphic-container">
        <div class="cube-3d">
          <div class="cube-face front"></div>
          <div class="cube-face back"></div>
          <div class="cube-face right"></div>
          <div class="cube-face left"></div>
          <div class="cube-face top"></div>
          <div class="cube-face bottom"></div>
        </div>
        <div class="cylinder-3d"></div>
        <div class="sphere-3d"></div>
      </div>
    </div>

    <!-- 右侧注册表单区域 -->
    <div class="right-section">
      <div class="register-form-container">
        <!-- Logo和标题 -->
        <div class="header">
          <div class="logo">
            <span class="logo-text">KirinChat</span>
          </div>
          <p class="subtitle">创建您的账户，开始智能对话之旅</p>
        </div>

        <!-- 注册表单 -->
        <div class="register-form">
          <div class="form-group">
            <label class="form-label">用户名</label>
            <HInput
              v-model="registerForm.user_name"
              placeholder="请输入用户名（最多20个字符）"
              size="large"
              class="register-input"
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-group">
            <label class="form-label">邮箱（可选）</label>
            <HInput
              v-model="registerForm.user_email"
              placeholder="请输入邮箱地址"
              size="large"
              class="register-input"
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <HInput
              v-model="registerForm.user_password"
              type="password"
              placeholder="请输入密码（至少6个字符）"
              size="large"
              class="register-input"
              :show-password="true"
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-group">
            <label class="form-label">确认密码</label>
            <HInput
              v-model="confirmPassword"
              type="password"
              placeholder="请再次输入密码"
              size="large"
              class="register-input"
              :show-password="true"
              @keyup.enter="handleRegister"
            />
          </div>

          <div class="form-actions">
            <div class="login-link">
              <span>已有账号？</span>
              <a href="#" @click="goToLogin">登录</a>
            </div>
          </div>

          <HButton
            type="primary"
            size="large"
            class="register-button"
            :loading="loading"
            @click="handleRegister"
          >
            注册
          </HButton>
        </div>

        <!-- 底部版本信息 -->
        <div class="footer">
          <div class="version-badge" title="KirinChat 版本">v2.5.0</div>
          <div class="footer-icons">
            <a href="https://github.com/kirintj/KirinChat" target="_blank" class="icon-link" title="GitHub">
              <img src="../../assets/github.png" alt="GitHub" class="icon-img" />
            </a>
            <a href="https://uawlh9wstr9.feishu.cn/wiki/QOaLwMDtBiiduWk4YtAcavEsnne" target="_blank" class="icon-link" title="帮助文档">
              <img src="../../assets/help.png" alt="帮助文档" class="icon-img" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.register-container {
  display: flex;
  height: 100vh;
  background: linear-gradient(135deg, var(--harmony-comp-background-tertiary) 0%, var(--harmony-comp-divider) 100%);
}

.left-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;

  .graphic-container {
    position: relative;
    width: 400px;
    height: 400px;
    
    .cube-3d {
      position: absolute;
      width: 120px;
      height: 120px;
      top: 50px;
      left: 100px;
      transform-style: preserve-3d;
      animation: rotateCube 10s infinite linear;

      .cube-face {
        position: absolute;
        width: 120px;
        height: 120px;
        background: linear-gradient(45deg, var(--harmony-brand), var(--harmony-interactive-pressed));
        border: 1px solid rgba(255, 255, 255, 0.2);
        
        &.front { transform: rotateY(0deg) translateZ(60px); }
        &.back { transform: rotateY(180deg) translateZ(60px); }
        &.right { transform: rotateY(90deg) translateZ(60px); }
        &.left { transform: rotateY(-90deg) translateZ(60px); }
        &.top { transform: rotateX(90deg) translateZ(60px); }
        &.bottom { transform: rotateX(-90deg) translateZ(60px); }
      }
    }

    .cylinder-3d {
      position: absolute;
      width: 80px;
      height: 160px;
      top: 200px;
      left: 50px;
      background: linear-gradient(180deg, #6b9eff, var(--harmony-brand));
      border-radius: 40px;
      box-shadow: 0 10px 30px rgba(79, 129, 255, 0.3);
      animation: floatUp 6s ease-in-out infinite;
    }

    .sphere-3d {
      position: absolute;
      width: 60px;
      height: 60px;
      top: 120px;
      right: 80px;
      background: radial-gradient(circle at 30% 30%, #8bb6ff, var(--harmony-brand));
      border-radius: 50%;
      box-shadow: 0 8px 25px rgba(79, 129, 255, 0.4);
      animation: floatDown 8s ease-in-out infinite;
    }
  }
}

.right-section {
  overflow: hidden;  // 加上这一行
  width: 450px;
  background: var(--harmony-comp-background-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: -2px 0 20px rgba(0, 0, 0, 0.1);

  .register-form-container {
    width: 320px;
    padding: 20px 0;

    .header {
      text-align: center;
      margin-bottom: 24px;

      .logo {
        margin-bottom: 16px;

        .logo-text {
          display: inline-block;
          background: linear-gradient(45deg, var(--harmony-brand), var(--harmony-interactive-pressed));
          color: white;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 20px;
          font-weight: 700;
          letter-spacing: 2px;
          font-family: var(--harmony-font-family);
          box-shadow: 0 4px 12px rgba(79, 129, 255, 0.3);
        }
      }

      .subtitle {
        color: var(--harmony-font-secondary);
        font-size: 16px;
        margin: 0;
        line-height: 1.6;
        font-weight: 400;
        font-family: var(--harmony-font-family);
      }
    }

    .register-form {
      .form-group {
        margin-bottom: 14px;

        .form-label {
          display: block;
          font-size: 16px;
          font-weight: 600;
          color: var(--harmony-font-primary);
          margin-bottom: 10px;
          font-family: var(--harmony-font-family);
          letter-spacing: 0.5px;
        }

        .register-input {
          :deep(.el-input__wrapper) {
            background: var(--harmony-comp-background-tertiary);
            border: 1px solid var(--harmony-comp-divider);
            border-radius: 8px;
            padding: 12px 16px;
            box-shadow: none;

            &:hover {
              border-color: var(--harmony-brand);
            }

            &.is-focus {
              border-color: var(--harmony-brand);
              box-shadow: 0 0 0 3px rgba(79, 129, 255, 0.1);
            }
          }

          :deep(.el-input__inner) {
            color: var(--harmony-font-primary);
            font-size: 16px;
            font-family: var(--harmony-font-family);
            font-weight: 400;

            &::placeholder {
              color: var(--harmony-font-tertiary);
              font-size: 15px;
            }
          }
        }
      }

      .form-actions {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 24px;

        .login-link {
          font-size: 15px;
          color: var(--harmony-font-secondary);
          font-family: var(--harmony-font-family);

          a {
            color: var(--harmony-brand);
            text-decoration: none;
            margin-left: 6px;
            font-weight: 500;
            transition: all 0.2s ease;

            &:hover {
              text-decoration: underline;
              color: var(--harmony-interactive-pressed);
            }
          }
        }
      }

      .register-button {
        width: 100%;
        height: 52px;
        background: linear-gradient(45deg, var(--harmony-brand), var(--harmony-interactive-pressed));
        border: none;
        border-radius: 10px;
        font-size: 18px;
        font-weight: 600;
        font-family: var(--harmony-font-family);
        letter-spacing: 1px;
        transition: all 0.3s ease;

        &:hover {
          transform: translateY(-1px);
          box-shadow: 0 8px 25px rgba(79, 129, 255, 0.3);
        }

        &:active {
          transform: translateY(0);
        }
      }
    }

    .footer {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-top: 20px;
      color: var(--harmony-font-tertiary);
      font-size: 13px;
      font-family: var(--harmony-font-family);
      font-weight: 400;
      border-top: 1px solid var(--harmony-comp-divider);
      padding-top: 16px;

      .version-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: 999px;
        background: var(--harmony-comp-emphasize-tertiary);
        color: var(--harmony-brand);
        border: 1px solid rgba(10, 89, 247, 0.25);
        font-weight: 600;
        letter-spacing: 0.3px;
      }

      .footer-icons {
        display: flex;
        gap: 10px;

        a {
          width: 28px;
          height: 28px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--harmony-comp-background-secondary);
          border: 1px solid var(--harmony-comp-divider);
          border-radius: 8px;
          transition: all 0.2s ease;
          overflow: hidden;

          &:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px rgba(10, 89, 247, 0.2);
            border-color: rgba(10, 89, 247, 0.4);
          }

          .icon-img {
            width: 18px;
            height: 18px;
            object-fit: contain;
            filter: saturate(0.9) contrast(1.05);
          }
        }
      }
    }
  }
}

@keyframes rotateCube {
  0% { transform: rotateX(0deg) rotateY(0deg); }
  100% { transform: rotateX(360deg) rotateY(360deg); }
}

@keyframes floatUp {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-15px); }
}

@keyframes floatDown {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(10px); }
}
</style> 