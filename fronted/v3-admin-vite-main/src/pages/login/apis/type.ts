export interface LoginRequestData {
  /** 邮箱或手机号 */
  account: string
  /** 密码 */
  password: string
}

export type LoginResponseData = ApiResponseData<{ user_id: number; tokens: { access: string; refresh: string } }>
