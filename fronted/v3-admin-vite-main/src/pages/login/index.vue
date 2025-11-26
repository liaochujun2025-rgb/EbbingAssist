<script lang="ts" setup>
import type { FormRules } from "element-plus"
import type { LoginRequestData } from "./apis/type"
import ThemeSwitch from "@@/components/ThemeSwitch/index.vue"
import { Lock, User } from "@element-plus/icons-vue"
import { useSettingsStore } from "@/pinia/stores/settings"
import { useUserStore } from "@/pinia/stores/user"
import { loginApi } from "./apis"
import Owl from "./components/Owl.vue"
import { useFocus } from "./composables/useFocus"

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const settingsStore = useSettingsStore()
const { isFocus, handleBlur, handleFocus } = useFocus()

const loginFormRef = useTemplateRef("loginFormRef")
const loading = ref(false)

const loginFormData: LoginRequestData = reactive({
  account: "",
  password: ""
})

const loginFormRules: FormRules = {
  account: [
    { required: true, message: "请输入邮箱或手机号", trigger: "blur" }
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 8, max: 32, message: "长度为 8 至 32 个字符", trigger: "blur" }
  ]
}

async function handleLogin() {
  loginFormRef.value?.validate(async (valid) => {
    if (!valid) {
      ElMessage.error("表单校验不通过")
      return
    }
    loading.value = true
    try {
      const { data } = await loginApi(loginFormData)
      userStore.setTokens(data.tokens)
      router.push(route.query.redirect ? decodeURIComponent(route.query.redirect as string) : "/")
    } catch (error) {
      loginFormData.password = ""
    } finally {
      loading.value = false
    }
  })
}
</script>

<template>
  <div class="login-container">
    <ThemeSwitch v-if="settingsStore.showThemeSwitch" class="theme-switch" />
    <Owl :close-eyes="isFocus" />
    <div class="login-card">
      <div class="title">
        <img src="@@/assets/images/layouts/logo-text-2.png" alt="Ebbing Assist">
      </div>
      <div class="content">
        <el-form ref="loginFormRef" :model="loginFormData" :rules="loginFormRules" @keyup.enter="handleLogin">
          <el-form-item prop="account">
            <el-input
              v-model.trim="loginFormData.account"
              placeholder="邮箱 / 手机号"
              type="text"
              tabindex="1"
              :prefix-icon="User"
              size="large"
            />
          </el-form-item>
          <el-form-item prop="password">
            <el-input
              v-model.trim="loginFormData.password"
              placeholder="密码"
              type="password"
              tabindex="2"
              :prefix-icon="Lock"
              size="large"
              show-password
              @blur="handleBlur"
              @focus="handleFocus"
            />
          </el-form-item>
          <el-button :loading="loading" type="primary" size="large" @click.prevent="handleLogin">
            登录
          </el-button>
        </el-form>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.login-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100%;
  min-height: 100%;
  .theme-switch {
    position: fixed;
    top: 5%;
    right: 5%;
    cursor: pointer;
  }
  .login-card {
    width: 480px;
    max-width: 90%;
    border-radius: 20px;
    box-shadow: 0 0 10px #dcdfe6;
    background-color: var(--el-bg-color);
    overflow: hidden;
    .title {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 150px;
      img {
        height: 100%;
      }
    }
    .content {
      padding: 20px 50px 50px 50px;
      .el-button {
        width: 100%;
        margin-top: 10px;
      }
    }
  }
}
</style>
