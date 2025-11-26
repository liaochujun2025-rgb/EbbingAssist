import type * as Plans from "./type"
import { request } from "@/http/axios"

export function listPlansApi(params: {
  status?: string
  priority?: string
  tag?: string
  start_date?: string
  end_date?: string
}) {
  return request<Plans.ListPlansResponse>({
    url: "/plans",
    method: "get",
    params
  })
}

export function getPlanDetailApi(id: number) {
  return request<Plans.PlanDetailResponse>({
    url: `/plans/${id}`,
    method: "get"
  })
}

export function createPlanApi(data: Partial<Plans.PlanItem>) {
  return request<Plans.PlanCreateResponse>({
    url: "/plans",
    method: "post",
    data
  })
}

export function updatePlanApi(id: number, data: Partial<Plans.PlanItem>) {
  return request<Plans.PlanCreateResponse>({
    url: `/plans/${id}`,
    method: "put",
    data
  })
}

export function deletePlanApi(id: number) {
  return request<ApiResponseData<null>>({
    url: `/plans/${id}`,
    method: "delete"
  })
}

export function createTaskApi(planId: number, data: Partial<Plans.TaskItem>) {
  return request<Plans.TaskCreateResponse>({
    url: `/plans/${planId}/tasks`,
    method: "post",
    data
  })
}

export function updateTaskApi(taskId: number, data: Partial<Plans.TaskItem>) {
  return request<Plans.TaskUpdateResponse>({
    url: `/tasks/${taskId}`,
    method: "put",
    data
  })
}

export function completeTaskApi(taskId: number) {
  return request<Plans.TaskUpdateResponse>({
    url: `/tasks/${taskId}/complete`,
    method: "post"
  })
}
