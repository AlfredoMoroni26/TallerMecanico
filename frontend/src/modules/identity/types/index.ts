export interface Role { id: string; name: string; description: string | null; is_system: boolean }
export interface User { id: string; username: string; email: string; is_active: boolean; created_at: string; roles: Role[] }
export interface TokenPair { access_token: string; refresh_token: string; token_type: 'bearer' }
export interface ApiError { detail?: string }
