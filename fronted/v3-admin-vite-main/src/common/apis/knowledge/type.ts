export interface Topic {
  id: number
  name: string
  desc?: string | null
  created_at: string
}

export interface KnowledgeEntry {
  id: number
  title: string
  content: string
  tags: string[]
  links: string[]
  topic_id?: number | null
  created_at: string
  updated_at: string
}

export interface StudyLog {
  id: number
  entry_id: number
  note?: string | null
  logged_at: string
  created_at: string
}

export type TopicListResponse = ApiResponseData<{ items: Topic[]; total: number }>
export type KnowledgeListResponse = ApiResponseData<{ items: KnowledgeEntry[]; total: number; page: number; page_size: number }>
export type KnowledgeDetailResponse = ApiResponseData<KnowledgeEntry>
export type KnowledgeMutateResponse = ApiResponseData<KnowledgeEntry>
export type StudyLogListResponse = ApiResponseData<{ items: StudyLog[]; total: number; start_date: string; end_date: string }>
export type StudyLogCreateResponse = ApiResponseData<StudyLog>
