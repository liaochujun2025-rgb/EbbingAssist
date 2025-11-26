import type { RouteRecordRaw } from "vue-router"
import { createRouter } from "vue-router"

import { routerConfig } from "@/router/config"
import { registerNavigationGuard } from "@/router/guard"
import { flatMultiLevelRoutes } from "./helper"

const Layouts = () => import("@/layouts/index.vue")

/**
 * 常驻路由（仅 MVP：登录/错误页 + 知识管理）
 */
export const constantRoutes: RouteRecordRaw[] = [
  {
    path: "/redirect",
    component: Layouts,
    meta: { hidden: true },
    children: [
      {
        path: ":path(.*)",
        component: () => import("@/pages/redirect/index.vue")
      }
    ]
  },
  {
    path: "/403",
    component: () => import("@/pages/error/403.vue"),
    meta: { hidden: true }
  },
  {
    path: "/404",
    component: () => import("@/pages/error/404.vue"),
    meta: { hidden: true },
    alias: "/:pathMatch(.*)*"
  },
  {
    path: "/login",
    component: () => import("@/pages/login/index.vue"),
    meta: { hidden: true }
  },
  {
    path: "/",
    component: Layouts,
    redirect: "/knowledge",
    children: [
      {
        path: "knowledge",
        component: () => import("@/pages/plan/index.vue"),
        name: "Knowledge",
        meta: {
          title: "知识管理",
          elIcon: "Collection",
          affix: true
        }
      }
    ]
  }
]

/**
 * 动态路由（MVP 暂空，预留未来版本）
 */
export const dynamicRoutes: RouteRecordRaw[] = []

export const router = createRouter({
  history: routerConfig.history,
  routes: routerConfig.thirdLevelRouteCache ? flatMultiLevelRoutes(constantRoutes) : constantRoutes
})

export function resetRouter() {
  try {
    router.getRoutes().forEach((route) => {
      const { name, meta } = route
      if (name && meta.roles?.length) {
        router.hasRoute(name) && router.removeRoute(name)
      }
    })
  } catch {
    location.reload()
  }
}

registerNavigationGuard(router)
