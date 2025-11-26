import type * as Knowledge from "./type"
import { request } from "@/http/axios"

export function listTopicsApi() {
  return request<Knowledge.TopicListResponse>({
    url: "/knowledge/topics",
    method: "get"
  })
}

export function createTopicApi(data: { name: string; desc?: string }) {
  return request<Knowledge.TopicListResponse>({
    url: "/knowledge/topics",
    method: "post",
    data
  })
}

export function updateTopicApi(id: number, data: { name?: string; desc?: string }) {
  return request<Knowledge.TopicListResponse>({
    url: `/knowledge/topics/${id}`,
    method: "put",
    data
  })
}

export function deleteTopicApi(id: number) {
  return request<ApiResponseData<null>>({
    url: `/knowledge/topics/${id}`,
    method: "delete"
  })
}

export function listEntriesApi(params: { keyword?: string; tag?: string; topic_id?: number; page?: number; page_size?: number }) {
  return request<Knowledge.KnowledgeListResponse>({
    url: "/knowledge/entries",
    method: "get",
    params
  })
}

export function createEntryApi(data: Partial<Knowledge.KnowledgeEntry>) {
  return request<Knowledge.KnowledgeMutateResponse>({
    url: "/knowledge/entries",
    method: "post",
    data
  })
}

export function updateEntryApi(id: number, data: Partial<Knowledge.KnowledgeEntry>) {
  return request<Knowledge.KnowledgeMutateResponse>({
    url: `/knowledge/entries/${id}`,
    method: "put",
    data
  })
}

export function deleteEntryApi(id: number) {
  return request<ApiResponseData<null>>({
    url: `/knowledge/entries/${id}`,
    method: "delete"
  })
}

export function listStudyLogsApi(params?: { start_date?: string; end_date?: string }) {
  return request<Knowledge.StudyLogListResponse>({
    url: "/study/logs",
    method: "get",
    params
  })
}

export function createStudyLogApi(data: { entry_id: number; note?: string; logged_at?: string }) {
  return request<Knowledge.StudyLogCreateResponse>({
    url: "/study/logs",
    method: "post",
    data
  })
}
