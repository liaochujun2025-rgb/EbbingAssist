import type { AxiosInstance, AxiosRequestConfig } from "axios"
import { ElMessage } from "element-plus"
import axios from "axios"
import { get, merge } from "lodash-es"

import { getToken } from "@/common/utils/cache/cookies"
import { useUserStore } from "@/pinia/stores/user"

function logout() {
  useUserStore().logout()
  location.reload()
}

function createInstance() {
  const instance = axios.create()

  instance.interceptors.response.use(
    (response) => {
      const apiData = response.data
      const responseType = response.config.responseType
      if (responseType === "blob" || responseType === "arraybuffer") return apiData
      const code = apiData.code
      if (code === undefined) {
        ElMessage.error("非本系统的接口")
        return Promise.reject(new Error("non-system-api"))
      }
      if (code === 0) return apiData
      if (code === 1002 || code === 2003) {
        logout()
        return Promise.reject(new Error("unauthorized"))
      }
      ElMessage.error(apiData.message || "请求失败")
      return Promise.reject(new Error(apiData.message || "request_error"))
    },
    (error) => {
      const status = get(error, "response.status")
      const message = get(error, "response.data.message")
      switch (status) {
        case 400:
          error.message = message || "请求错误"
          break
        case 401:
          error.message = message || "未授权"
          logout()
          break
        case 403:
          error.message = message || "拒绝访问"
          break
        case 404:
          error.message = "请求地址出错"
          break
        case 408:
          error.message = "请求超时"
          break
        case 500:
          error.message = "服务器内部错误"
          break
        default:
          error.message = message || "请求失败"
      }
      ElMessage.error(error.message)
      return Promise.reject(error)
    }
  )
  return instance
}

function createRequest(instance: AxiosInstance) {
  return <T>(config: AxiosRequestConfig): Promise<T> => {
    const token = getToken()
    const defaultConfig: AxiosRequestConfig = {
      baseURL: import.meta.env.VITE_BASE_URL,
      headers: {
        Authorization: token ? `Bearer ${token}` : undefined,
        "Content-Type": "application/json",
      },
      data: {},
      timeout: 8000,
      withCredentials: false,
    }
    const mergeConfig = merge(defaultConfig, config)
    return instance(mergeConfig)
  }
}

const instance = createInstance()
export const request = createRequest(instance)
