<script lang="ts" setup>
import dayjs from "dayjs"
import { ElMessageBox } from "element-plus"

import type { FormInstance, FormRules } from "element-plus"
import type { KnowledgeEntry, StudyLog, Topic } from "@@/apis/knowledge/type"
import {
  createEntryApi,
  createStudyLogApi,
  createTopicApi,
  deleteEntryApi,
  listEntriesApi,
  listStudyLogsApi,
  listTopicsApi,
  updateEntryApi
} from "@@/apis/knowledge"

const loading = ref(false)
const entries = ref<KnowledgeEntry[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const topics = ref<Topic[]>([])

const filters = reactive({
  keyword: "",
  tag: "",
  topic_id: undefined as number | undefined
})

const entryDialogVisible = ref(false)
const entryFormRef = ref<FormInstance>()
const entryForm = reactive<Partial<KnowledgeEntry>>({
  id: undefined,
  title: "",
  content: "",
  tags: [],
  topic_id: undefined
})

const entryRules: FormRules = {
  title: [{ required: true, message: "请输入标题", trigger: "blur" }],
  content: [{ required: true, message: "请输入内容", trigger: "blur" }]
}

const studyDialogVisible = ref(false)
const studyFormRef = ref<FormInstance>()
const studyForm = reactive<{ entry_id: number | null; note: string; logged_at: string }>({
  entry_id: null,
  note: "",
  logged_at: dayjs().format("YYYY-MM-DD")
})
const studyLogs = ref<StudyLog[]>([])

async function fetchTopics() {
  const { data } = await listTopicsApi()
  topics.value = data.items
}

async function fetchEntries() {
  loading.value = true
  try {
    const { data } = await listEntriesApi({
      keyword: filters.keyword || undefined,
      tag: filters.tag || undefined,
      topic_id: filters.topic_id,
      page: page.value,
      page_size: pageSize.value
    })
    entries.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

function openCreateEntry() {
  Object.assign(entryForm, { id: undefined, title: "", content: "", tags: [], topic_id: undefined })
  entryDialogVisible.value = true
}

function openEditEntry(row: KnowledgeEntry) {
  Object.assign(entryForm, {
    id: row.id,
    title: row.title,
    content: row.content,
    tags: row.tags || [],
    topic_id: row.topic_id || undefined
  })
  entryDialogVisible.value = true
}

async function submitEntry() {
  if (!entryFormRef.value) return
  await entryFormRef.value.validate()
  const payload = {
    title: entryForm.title,
    content: entryForm.content,
    tags: entryForm.tags || [],
    topic_id: entryForm.topic_id
  }
  if (entryForm.id) {
    await updateEntryApi(entryForm.id, payload)
  } else {
    await createEntryApi(payload)
  }
  entryDialogVisible.value = false
  await fetchEntries()
}

async function removeEntry(row: KnowledgeEntry) {
  await ElMessageBox.confirm(`确认删除知识条目「${row.title}」？`, "删除确认", { type: "warning" })
  await deleteEntryApi(row.id)
  await fetchEntries()
}

async function addTopic(name: string) {
  if (!name.trim()) return
  await createTopicApi({ name })
  await fetchTopics()
}

function openStudyDialog(entry: KnowledgeEntry) {
  studyDialogVisible.value = true
  studyForm.entry_id = entry.id
  studyForm.note = ""
  studyForm.logged_at = dayjs().format("YYYY-MM-DD")
}

async function submitStudyLog() {
  if (!studyForm.entry_id) return
  if (!studyFormRef.value) return
  await studyFormRef.value.validate()
  await createStudyLogApi({
    entry_id: studyForm.entry_id,
    note: studyForm.note || "",
    logged_at: studyForm.logged_at
  })
  studyDialogVisible.value = false
  await fetchStudyLogs()
}

async function fetchStudyLogs() {
  const { data } = await listStudyLogsApi()
  studyLogs.value = data.items
}

function handleSizeChange(val: number) {
  pageSize.value = val
  page.value = 1
  fetchEntries()
}

function handleCurrentChange(val: number) {
  page.value = val
  fetchEntries()
}

onMounted(() => {
  fetchTopics()
  fetchEntries()
  fetchStudyLogs()
})
</script>

<template>
  <div class="page-wrapper">
    <el-card shadow="never" class="filter-card">
      <el-space wrap>
        <el-input v-model.trim="filters.keyword" placeholder="搜索标题或内容" style="width: 220px" clearable @change="fetchEntries" />
        <el-input v-model.trim="filters.tag" placeholder="标签" style="width: 140px" clearable @change="fetchEntries" />
        <el-select v-model="filters.topic_id" placeholder="主题" clearable style="width: 160px" @change="fetchEntries">
          <el-option v-for="t in topics" :key="t.id" :label="t.name" :value="t.id" />
        </el-select>
        <el-button type="primary" @click="openCreateEntry">新建条目</el-button>
        <el-button @click="fetchEntries">刷新</el-button>
      </el-space>
    </el-card>

    <el-card shadow="never">
      <el-table :data="entries" v-loading="loading" stripe>
        <el-table-column prop="title" label="标题" min-width="200">
          <template #default="{ row }">
            <div class="title-cell">
              <div class="title-text">{{ row.title }}</div>
              <div class="meta">
                <span>更新：{{ dayjs(row.updated_at).format("MM-DD HH:mm") }}</span>
                <span v-if="row.topic_id">主题：{{ topics.find(t => t.id === row.topic_id)?.name || "-" }}</span>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="标签" min-width="160">
          <template #default="{ row }">
            <el-space wrap>
              <el-tag v-for="tag in row.tags" :key="tag" size="small" effect="plain">{{ tag }}</el-tag>
            </el-space>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="primary" @click="openEditEntry(row)">编辑</el-button>
              <el-button link type="success" @click="openStudyDialog(row)">学习记录</el-button>
              <el-button link type="danger" @click="removeEntry(row)">删除</el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination">
        <el-pagination
          background
          layout="prev, pager, next, sizes"
          :total="total"
          :current-page="page"
          :page-sizes="[10, 20, 50]"
          :page-size="pageSize"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <el-card shadow="never" class="study-card">
      <template #header>
        <div class="card-header">
          <span>近 7 天学习记录</span>
          <el-button size="small" @click="fetchStudyLogs">刷新</el-button>
        </div>
      </template>
      <el-timeline>
        <el-timeline-item
          v-for="log in studyLogs"
          :key="log.id"
          :timestamp="log.logged_at"
          placement="top"
        >
          <div class="log-item">
            <div>条目 ID：{{ log.entry_id }}</div>
            <div class="log-note">{{ log.note || "（无备注）" }}</div>
          </div>
        </el-timeline-item>
      </el-timeline>
    </el-card>

    <el-dialog v-model="entryDialogVisible" :title="entryForm.id ? '编辑条目' : '新建条目'" width="640px">
      <el-form ref="entryFormRef" :model="entryForm" :rules="entryRules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="entryForm.title" placeholder="标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="entryForm.content" type="textarea" rows="6" placeholder="内容" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="entryForm.tags"
            multiple
            filterable
            allow-create
            default-first-option
            placeholder="输入标签后回车添加"
            style="width: 100%"
          >
            <el-option v-for="tag in entryForm.tags as string[]" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
        <el-form-item label="主题">
          <el-select
            v-model="entryForm.topic_id"
            filterable
            allow-create
            default-first-option
            placeholder="选择或输入主题"
            style="width: 100%"
            @change="(val) => typeof val === 'string' ? addTopic(val) : undefined"
          >
            <el-option v-for="t in topics" :key="t.id" :label="t.name" :value="t.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="entryDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitEntry">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="studyDialogVisible" title="记录学习" width="420px">
      <el-form ref="studyFormRef" :model="studyForm" label-width="90px">
        <el-form-item label="日期">
          <el-date-picker v-model="studyForm.logged_at" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="studyForm.note" type="textarea" rows="3" placeholder="今天学了什么..." />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="studyDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitStudyLog">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.page-wrapper {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.filter-card {
  .el-space {
    width: 100%;
  }
}
.title-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
  .title-text {
    font-weight: 600;
  }
  .meta {
    display: flex;
    gap: 12px;
    color: var(--el-text-color-secondary);
    font-size: 12px;
  }
}
.pagination {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
.study-card {
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .log-item {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .log-note {
    color: var(--el-text-color-secondary);
  }
}
</style>
