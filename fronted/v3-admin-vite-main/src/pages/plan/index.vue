<script lang="ts" setup>
import dayjs from "dayjs"
import { ElMessageBox } from "element-plus"

import type { FormInstance, FormRules } from "element-plus"
import type { PlanItem, TaskItem } from "@@/apis/plans/type"
import { completeTaskApi, createPlanApi, createTaskApi, deletePlanApi, getPlanDetailApi, listPlansApi, updatePlanApi, updateTaskApi } from "@@/apis/plans"

const loading = ref(false)
const list = ref<PlanItem[]>([])
const activeTab = ref<"list" | "calendar">("list")
const filters = reactive({
  status: "",
  priority: "",
  tag: "",
  dateRange: [] as string[]
})

const statusOptions = [
  { label: "未开始", value: "not_started", type: "info" },
  { label: "进行中", value: "in_progress", type: "primary" },
  { label: "已完成", value: "completed", type: "success" },
  { label: "延期", value: "delayed", type: "danger" }
]
const taskStatusOptions = [
  { label: "待办", value: "todo", type: "info" },
  { label: "进行中", value: "doing", type: "primary" },
  { label: "已完成", value: "done", type: "success" },
  { label: "阻塞", value: "blocked", type: "warning" },
  { label: "延期", value: "delayed", type: "danger" }
]
const priorityOptions = [
  { label: "高", value: "high" },
  { label: "中", value: "medium" },
  { label: "低", value: "low" }
]

const planDialogVisible = ref(false)
const planFormRef = ref<FormInstance>()
const planForm = reactive<Partial<PlanItem>>({
  id: undefined,
  title: "",
  goal: "",
  deadline: "",
  priority: "medium",
  tags: []
})

const planRules: FormRules = {
  title: [{ required: true, message: "请输入计划标题", trigger: "blur" }],
  priority: [{ required: true, message: "请选择优先级", trigger: "change" }]
}

const taskDialogVisible = ref(false)
const taskFormRef = ref<FormInstance>()
const taskForm = reactive<Partial<TaskItem>>({
  plan_id: undefined,
  title: "",
  desc: "",
  estimate_minutes: undefined,
  priority: "medium",
  status: "todo",
  due_date: "",
  tags: []
})

const taskRules: FormRules = {
  title: [{ required: true, message: "请输入任务标题", trigger: "blur" }]
}

const detailDrawerVisible = ref(false)
const detailLoading = ref(false)
const activePlan = ref<PlanItem | null>(null)
const tasks = ref<TaskItem[]>([])

async function fetchPlans() {
  loading.value = true
  const params: Record<string, string> = {}
  if (filters.status) params.status = filters.status
  if (filters.priority) params.priority = filters.priority
  if (filters.tag) params.tag = filters.tag
  if (filters.dateRange.length === 2) {
    params.start_date = filters.dateRange[0]
    params.end_date = filters.dateRange[1]
  }
  try {
    const { data } = await listPlansApi(params)
    list.value = data.items
  } finally {
    loading.value = false
  }
}

function openCreatePlan() {
  Object.assign(planForm, { id: undefined, title: "", goal: "", deadline: "", priority: "medium", tags: [] })
  planDialogVisible.value = true
}

function openEditPlan(row: PlanItem) {
  Object.assign(planForm, {
    id: row.id,
    title: row.title,
    goal: row.goal,
    deadline: row.deadline,
    priority: row.priority,
    tags: row.tags
  })
  planDialogVisible.value = true
}

async function submitPlan() {
  if (!planFormRef.value) return
  await planFormRef.value.validate()
  const payload = {
    title: planForm.title,
    goal: planForm.goal,
    deadline: planForm.deadline || undefined,
    priority: planForm.priority,
    tags: planForm.tags || []
  }
  if (planForm.id) {
    await updatePlanApi(planForm.id, payload)
  } else {
    await createPlanApi(payload)
  }
  planDialogVisible.value = false
  await fetchPlans()
}

async function removePlan(row: PlanItem) {
  await ElMessageBox.confirm(`确认删除计划「${row.title}」？`, "删除确认", { type: "warning" })
  await deletePlanApi(row.id)
  await fetchPlans()
}

async function openDetail(row: PlanItem) {
  detailDrawerVisible.value = true
  detailLoading.value = true
  activePlan.value = row
  try {
    const { data } = await getPlanDetailApi(row.id)
    activePlan.value = data as PlanItem
    tasks.value = data.tasks || []
  } finally {
    detailLoading.value = false
  }
}

function openCreateTask(planId: number) {
  Object.assign(taskForm, {
    plan_id: planId,
    title: "",
    desc: "",
    estimate_minutes: undefined,
    priority: "medium",
    status: "todo",
    due_date: "",
    tags: []
  })
  taskDialogVisible.value = true
}

async function submitTask() {
  if (!taskFormRef.value) return
  await taskFormRef.value.validate()
  if (!taskForm.plan_id) return
  const payload = {
    title: taskForm.title,
    desc: taskForm.desc,
    estimate_minutes: taskForm.estimate_minutes,
    priority: taskForm.priority,
    status: taskForm.status,
    due_date: taskForm.due_date || undefined,
    tags: taskForm.tags || []
  }
  await createTaskApi(taskForm.plan_id, payload)
  taskDialogVisible.value = false
  await refreshDetail(taskForm.plan_id)
  await fetchPlans()
}

async function refreshDetail(planId: number) {
  const { data } = await getPlanDetailApi(planId)
  activePlan.value = data as PlanItem
  tasks.value = data.tasks || []
}

async function toggleTaskDone(task: TaskItem) {
  if (task.status === "done") return
  await completeTaskApi(task.id)
  if (activePlan.value) {
    await refreshDetail(activePlan.value.id)
    await fetchPlans()
  }
}

async function updateTaskStatus(task: TaskItem, status: string) {
  await updateTaskApi(task.id, { status })
  if (activePlan.value) {
    await refreshDetail(activePlan.value.id)
    await fetchPlans()
  }
}

const calendarValue = ref(new Date())

const planListForCalendar = computed(() => {
  return list.value.map((item) => ({
    ...item,
    deadlineDate: item.deadline ? dayjs(item.deadline).format("YYYY-MM-DD") : ""
  }))
})

onMounted(() => {
  fetchPlans()
})
</script>

<template>
  <div class="page-wrapper">
    <el-card class="filter-card" shadow="never">
      <div class="filter-row">
        <el-space wrap>
          <el-select v-model="filters.status" placeholder="状态" clearable style="width: 140px" @change="fetchPlans">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <el-select v-model="filters.priority" placeholder="优先级" clearable style="width: 140px" @change="fetchPlans">
            <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
          <el-input v-model.trim="filters.tag" placeholder="标签筛选" style="width: 160px" clearable @change="fetchPlans" />
          <el-date-picker
            v-model="filters.dateRange"
            type="daterange"
            value-format="YYYY-MM-DD"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="fetchPlans"
          />
          <el-button type="primary" @click="openCreatePlan">新建计划</el-button>
          <el-button @click="fetchPlans">刷新</el-button>
        </el-space>
      </div>
    </el-card>

    <el-card shadow="never" class="content-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="列表视图" name="list">
          <el-table :data="list" v-loading="loading" stripe style="width: 100%">
            <el-table-column prop="title" label="计划" min-width="160">
              <template #default="{ row }">
                <el-space>
                  <el-tag v-if="row.priority === 'high'" type="danger">高</el-tag>
                  <el-tag v-else-if="row.priority === 'medium'" type="info">中</el-tag>
                  <el-tag v-else type="success">低</el-tag>
                  <span class="plan-title">{{ row.title }}</span>
                </el-space>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="statusOptions.find(s => s.value === row.status)?.type || 'info'">
                  {{ statusOptions.find(s => s.value === row.status)?.label || row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="进度" width="160">
              <template #default="{ row }">
                <el-progress :percentage="Math.round((row.progress || 0) * 100)" :stroke-width="12" />
              </template>
            </el-table-column>
            <el-table-column prop="deadline" label="截止日期" width="140">
              <template #default="{ row }">
                <span>{{ row.deadline ? dayjs(row.deadline).format("MM-DD") : "-" }}</span>
              </template>
            </el-table-column>
            <el-table-column label="标签" min-width="180">
              <template #default="{ row }">
                <el-space wrap>
                  <el-tag v-for="tag in row.tags" :key="tag" type="info" effect="plain" size="small">{{ tag }}</el-tag>
                </el-space>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-space>
                  <el-button link type="primary" @click="openDetail(row)">详情</el-button>
                  <el-button link type="primary" @click="openEditPlan(row)">编辑</el-button>
                  <el-button link type="danger" @click="removePlan(row)">删除</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="日历视图" name="calendar">
          <el-calendar v-model="calendarValue">
            <template #date-cell="{ data }">
              <div class="calendar-cell">
                <span class="date-text">{{ data.day.split("-").slice(1).join("/") }}</span>
                <div class="calendar-badges">
                  <el-tag
                    v-for="plan in planListForCalendar.filter(p => p.deadlineDate === data.day)"
                    :key="plan.id"
                    type="danger"
                    size="small"
                    @click="openDetail(plan)"
                  >
                    {{ plan.title }}
                  </el-tag>
                </div>
              </div>
            </template>
          </el-calendar>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="planDialogVisible" :title="planForm.id ? '编辑计划' : '新建计划'" width="520px">
      <el-form ref="planFormRef" :model="planForm" :rules="planRules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="planForm.title" placeholder="计划标题" />
        </el-form-item>
        <el-form-item label="目标">
          <el-input v-model="planForm.goal" placeholder="计划目标/说明" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="planForm.deadline" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="planForm.priority" placeholder="优先级" style="width: 180px">
            <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="planForm.tags" multiple placeholder="添加标签" style="width: 100%">
            <el-option v-for="tag in planForm.tags as string[]" :key="tag" :label="tag" :value="tag" />
          </el-select>
          <div class="hint">直接在输入框输入标签后回车添加</div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="planDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitPlan">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="taskDialogVisible" title="新增任务" width="520px">
      <el-form ref="taskFormRef" :model="taskForm" :rules="taskRules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="taskForm.title" placeholder="任务标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="taskForm.desc" type="textarea" rows="2" placeholder="任务描述" />
        </el-form-item>
        <el-form-item label="预估时间">
          <el-input-number v-model="taskForm.estimate_minutes" :min="0" :step="15" /> 分钟
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="taskForm.priority" style="width: 180px">
            <el-option v-for="item in priorityOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="taskForm.status" style="width: 180px">
            <el-option v-for="item in taskStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期">
          <el-date-picker v-model="taskForm.due_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="taskForm.tags" multiple placeholder="添加标签" style="width: 100%">
            <el-option v-for="tag in taskForm.tags as string[]" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTask">保存</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailDrawerVisible" title="计划详情" size="55%" :destroy-on-close="true">
      <div v-if="activePlan" class="detail-header">
        <div class="detail-title">
          <span class="plan-title">{{ activePlan.title }}</span>
          <el-tag :type="statusOptions.find(s => s.value === activePlan.status)?.type || 'info'">
            {{ statusOptions.find(s => s.value === activePlan.status)?.label }}
          </el-tag>
        </div>
        <div class="detail-meta">
          <span>目标：{{ activePlan.goal || "—" }}</span>
          <span>截止：{{ activePlan.deadline ? dayjs(activePlan.deadline).format("YYYY-MM-DD") : "—" }}</span>
        </div>
        <el-progress :percentage="Math.round((activePlan.progress || 0) * 100)" :stroke-width="16" />
        <el-space style="margin-top: 8px;">
          <el-button type="primary" @click="openCreateTask(activePlan.id)">新增任务</el-button>
          <el-button @click="refreshDetail(activePlan.id)">刷新</el-button>
        </el-space>
      </div>
      <el-table :data="tasks" v-loading="detailLoading" stripe style="margin-top: 16px;">
        <el-table-column prop="title" label="任务" min-width="160">
          <template #default="{ row }">
            <div class="task-title">
              <el-tag size="small" effect="plain">{{ row.priority || "中" }}</el-tag>
              <span>{{ row.title }}</span>
            </div>
            <div class="task-desc">{{ row.desc }}</div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="130">
          <template #default="{ row }">
            <el-select v-model="row.status" size="small" @change="(val) => updateTaskStatus(row, val as string)">
              <el-option v-for="item in taskStatusOptions" :key="item.value" :label="item.label" :value="item.value" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="截止" width="120">
          <template #default="{ row }">
            {{ row.due_date ? dayjs(row.due_date).format("MM-DD") : "-" }}
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="160">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="tag in row.tags" :key="tag" size="small" effect="plain">{{ tag }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" size="small" :disabled="row.status === 'done'" @click="toggleTaskDone(row)">
              完成
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-drawer>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.filter-card {
  .filter-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}
.content-card {
  .plan-title {
    font-weight: 600;
  }
  .calendar-cell {
    min-height: 70px;
  }
  .calendar-badges {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-top: 4px;
  }
  .date-text {
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}
.detail-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.detail-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 18px;
}
.detail-meta {
  display: flex;
  gap: 16px;
  color: var(--el-text-color-secondary);
}
.task-title {
  display: flex;
  align-items: center;
  gap: 6px;
}
.task-desc {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
.hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
  margin-left: 8px;
}
</style>
