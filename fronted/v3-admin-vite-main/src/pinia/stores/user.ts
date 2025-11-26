import { getCurrentUserApi } from "@@/apis/users"
import { getRefreshToken, getToken, removeRefreshToken, removeToken, setRefreshToken as _setRefreshToken, setToken as _setToken } from "@@/utils/cache/cookies"
import { pinia } from "@/pinia"
import { resetRouter } from "@/router"
import { routerConfig } from "@/router/config"
import { useSettingsStore } from "./settings"
import { useTagsViewStore } from "./tags-view"

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(getToken() || "")
  const refreshToken = ref<string>(getRefreshToken() || "")

  const roles = ref<string[]>([])

  const username = ref<string>("")
  const nickname = ref<string>("")

  const tagsViewStore = useTagsViewStore()

  const settingsStore = useSettingsStore()

  // 设置 Token
  const setTokens = (value: { access: string; refresh: string }) => {
    _setToken(value.access)
    _setRefreshToken(value.refresh)
    token.value = value.access
    refreshToken.value = value.refresh
  }

  // 获取用户详情
  const getInfo = async () => {
    const { data } = await getCurrentUserApi()
    username.value = data.email
    nickname.value = data.nickname
    roles.value = data.roles?.length > 0 ? data.roles : routerConfig.defaultRoles
  }

  // 模拟角色变化
  const changeRoles = (role: string) => {
    const newToken = `token-${role}`
    token.value = newToken
    _setToken(newToken)
    // 用刷新页面代替重新登录
    location.reload()
  }

  // 登出
  const logout = () => {
    removeToken()
    removeRefreshToken()
    token.value = ""
    refreshToken.value = ""
    roles.value = []
    resetRouter()
    resetTagsView()
  }

  // 重置 Token
  const resetToken = () => {
    removeToken()
    removeRefreshToken()
    token.value = ""
    refreshToken.value = ""
    roles.value = []
  }

  // 重置 Visited Views 和 Cached Views
  const resetTagsView = () => {
    if (!settingsStore.cacheTagsView) {
      tagsViewStore.delAllVisitedViews()
      tagsViewStore.delAllCachedViews()
    }
  }

  return { token, refreshToken, roles, username, nickname, setTokens, getInfo, changeRoles, logout, resetToken }
})

/**
 * @description 在 SPA 应用中可用于在 pinia 实例被激活前使用 store
 * @description 在 SSR 应用中可用于在 setup 外使用 store
 */
export function useUserStoreOutside() {
  return useUserStore(pinia)
}
