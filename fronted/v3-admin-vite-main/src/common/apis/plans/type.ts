export type PlanStatus = "not_started" | "in_progress" | "completed" | "delayed"
export type TaskStatus = "todo" | "doing" | "done" | "blocked" | "delayed"

export interface PlanItem {
  id: number
  title: string
  goal?: string | null
  deadline?: string | null
  priority: string
  tags: string[]
  status: PlanStatus
  progress: number
  created_at: string
  updated_at: string
}

export interface TaskItem {
  id: number
  plan_id: number
  title: string
  desc?: string | null
  estimate_minutes?: number | null
  priority: string
  status: TaskStatus
  due_date?: string | null
  tags: string[]
  order_no: number
  focus_minutes: number
  created_at: string
  updated_at: string
}

export type ListPlansResponse = ApiResponseData<{ items: PlanItem[]; total: number }>
export type PlanDetailResponse = ApiResponseData<PlanItem & { tasks: TaskItem[] }>
export type PlanCreateResponse = ApiResponseData<PlanItem>
export type TaskCreateResponse = ApiResponseData<TaskItem>
export type TaskUpdateResponse = ApiResponseData<TaskItem>
