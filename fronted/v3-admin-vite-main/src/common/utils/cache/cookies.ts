// 统一处理 Cookie

import { CacheKey } from "@@/constants/cache-key"
import Cookies from "js-cookie"

export function getToken() {
  return Cookies.get(CacheKey.TOKEN)
}

export function setToken(token: string) {
  Cookies.set(CacheKey.TOKEN, token)
}

export function removeToken() {
  Cookies.remove(CacheKey.TOKEN)
}

export function getRefreshToken() {
  return Cookies.get(CacheKey.REFRESH_TOKEN)
}

export function setRefreshToken(token: string) {
  Cookies.set(CacheKey.REFRESH_TOKEN, token)
}

export function removeRefreshToken() {
  Cookies.remove(CacheKey.REFRESH_TOKEN)
}
