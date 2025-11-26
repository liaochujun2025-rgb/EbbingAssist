import { flushPromises, mount } from "@vue/test-utils"
import { defineComponent, h } from "vue"
import { describe, expect, it, beforeEach, vi } from "vitest"

import KnowledgePage from "@/pages/plan/index.vue"

vi.mock("@/common/apis/knowledge", () => {
  const topics = [{ id: 1, name: "Topic1", desc: "", created_at: "2024-01-01" }]
  const entries = [
    {
      id: 1,
      title: "Entry1",
      content: "content",
      tags: ["tag1"],
      links: [],
      topic_id: 1,
      created_at: "2024-01-01",
      updated_at: "2024-01-02"
    }
  ]
  const logs = [
    {
      id: 1,
      entry_id: 1,
      note: "today",
      logged_at: "2024-01-02",
      created_at: "2024-01-02"
    }
  ]
  return {
    listTopicsApi: vi.fn().mockResolvedValue({ data: { items: topics, total: topics.length } }),
    listEntriesApi: vi.fn().mockResolvedValue({
      data: { items: entries, total: entries.length, page: 1, page_size: 10 }
    }),
    listStudyLogsApi: vi.fn().mockResolvedValue({
      data: { items: logs, total: logs.length, start_date: "2024-01-01", end_date: "2024-01-02" }
    }),
    createEntryApi: vi.fn().mockResolvedValue({ data: entries[0] }),
    updateEntryApi: vi.fn().mockResolvedValue({ data: entries[0] }),
    deleteEntryApi: vi.fn().mockResolvedValue({ data: null }),
    createStudyLogApi: vi.fn().mockResolvedValue({ data: logs[0] })
  }
})

// Simple Element Plus stubs to render slots
const elStub = (tag = "div") => ({ template: `<${tag}><slot/></${tag}>` })
const ElTable = defineComponent({
  props: { data: { type: Array, default: () => [] } },
  setup(props, { slots }) {
    return () =>
      h(
        "div",
        {},
        (props.data as any[]).map((row, index) => (slots.default ? slots.default({ row, $index: index }) : null))
      )
  }
})
const ElTableColumn = defineComponent({
  setup(_props, { slots }) {
    return () => h("div", {}, slots.default ? slots.default({ row: {}, $index: 0 }) : null)
  }
})
const globalStubs = {
  "el-card": elStub(),
  "el-space": elStub(),
  "el-input": elStub(),
  "el-select": elStub(),
  "el-option": elStub(),
  "el-button": elStub("button"),
  "el-table": ElTable,
  "el-table-column": ElTableColumn,
  "el-pagination": elStub(),
  "el-timeline": elStub(),
  "el-timeline-item": elStub(),
  "el-dialog": elStub(),
  "el-form": elStub(),
  "el-form-item": elStub(),
  "el-date-picker": elStub(),
  "el-input-number": elStub()
}

const apis = await import("@/common/apis/knowledge")

describe("Knowledge page", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("loads entries and study logs on mount", async () => {
    const wrapper = mount(KnowledgePage, { global: { stubs: globalStubs } })
    await flushPromises()
    expect(apis.listEntriesApi).toHaveBeenCalled()
    expect(apis.listStudyLogsApi).toHaveBeenCalled()
    expect(wrapper.exists()).toBe(true)
  })

  it("submits a new entry and study log", async () => {
    const wrapper = mount(KnowledgePage, { global: { stubs: globalStubs } })
    await flushPromises()
    ;(wrapper.vm as any).entryFormRef.value = { validate: vi.fn().mockResolvedValue(true) }
    ;(wrapper.vm as any).entryForm.title = "New"
    ;(wrapper.vm as any).entryForm.content = "Content"
    await (wrapper.vm as any).submitEntry()
    expect(apis.createEntryApi).toHaveBeenCalled()

    ;(wrapper.vm as any).studyFormRef.value = { validate: vi.fn().mockResolvedValue(true) }
    ;(wrapper.vm as any).studyForm.entry_id = 1
    await (wrapper.vm as any).submitStudyLog()
    expect(apis.createStudyLogApi).toHaveBeenCalled()
  })
})
