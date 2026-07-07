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
  <div class="login-container">
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

    <!-- 右侧登录表单区域 -->
    <div class="right-section">
      <div class="login-form-container">
        <!-- Logo和标题 -->
        <div class="header">
          <div class="logo">
            <span class="logo-text">KirinChat</span>
          </div>
          <p class="subtitle">更智能、更多元的大模型应用开发平台</p>
        </div>

        <!-- 登录表单 -->
        <div class="login-form">
          <div class="form-group">
            <label class="form-label">账号</label>
            <HInput
              v-model="loginForm.username"
              placeholder="请输入账号"
              size="large"
              class="login-input"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="form-group">
            <label class="form-label">密码</label>
            <HInput
              v-model="loginForm.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              class="login-input"
              :show-password="true"
              @keyup.enter="handleLogin"
            />
          </div>

          <div class="form-actions">
            <div class="register-link">
              <span>没有账号？</span>
              <a href="#" @click="goToRegister">注册</a>
            </div>
          </div>

          <HButton
            type="primary"
            size="large"
            class="login-button"
            :loading="loading"
            @click="handleLogin"
          >
            登录
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
.login-container {
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
  width: 450px;
  background: var(--harmony-comp-background-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: -2px 0 20px rgba(0, 0, 0, 0.1);

  .login-form-container {
    width: 320px;
    padding: 40px 0;

    .header {
      text-align: center;
      margin-bottom: 40px;

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

    .login-form {
      .form-group {
        margin-bottom: 20px;

        .form-label {
          display: block;
          font-size: 16px;
          font-weight: 600;
          color: var(--harmony-font-primary);
          margin-bottom: 10px;
          font-family: var(--harmony-font-family);
          letter-spacing: 0.5px;
        }

        .login-input {
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

        .register-link {
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

      .login-button {
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
      margin-top: 36px;
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

@keyframes floatUp {
  0%, 100% { transform: translateY(0px); }

@keyframes floatDown {
  0%, 100% { transform: translateY(0px); }

</style>