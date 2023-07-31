declare namespace USER_MANAGE_API {
  type User = {
    nickname: string;
    avatar?: string;
    id: number;
    email?: string;
    phone_number?: string;
    disabled: boolean;
    username: string;
    organization: ORGANIZATION_API.Organization;
    organization_id: number;
    role: ROLE_API.Role;
    role_id: number;
  };

  type UserUpdate = {
    nickname: string;
    id: number;
    email?: string;
    phone_number?: string;
    organization_id: number;
    role_id: number;
    disabled: boolean;
  };

  type UserCreate = Omit<UserUpdate, 'id'>;

  type AllUserRes = DEFAULT_API.Paginate<User>;
}
