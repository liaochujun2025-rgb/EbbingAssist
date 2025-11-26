export type CurrentUserResponseData = ApiResponseData<{
  id: number
  email: string
  nickname: string
  avatar?: string | null
  timezone?: string
  roles: string[]
  prefs?: Record<string, unknown>
}>
