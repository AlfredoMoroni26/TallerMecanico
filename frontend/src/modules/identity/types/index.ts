export interface RoleStatus { id_estatus: number; nombre_estatus: string }
export interface Role { id: string; id_rol: number; name: string; description: string | null; is_system: boolean; id_estatus: number; estatus: RoleStatus }
export interface User { id: string; username: string; email: string; is_active: boolean; workshop_id: string | null; created_at: string; roles: Role[] }
export interface TokenPair { access_token: string; refresh_token: string; token_type: 'bearer' }
export interface ApiError { detail?: string }
