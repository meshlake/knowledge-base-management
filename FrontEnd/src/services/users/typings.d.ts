declare namespace USER_API {
  type LoginResult = {
    status?: string;
    type?: string;
    currentAuthority?: string;
    access_token: string;
    token_type: string;
    user_role: ROLE_API.Role;
  };

  type CurrentUser = {
    nickname?: string;
    avatar?: string;
    userid?: string;
    email?: string;
    signature?: string;
    title?: string;
    group?: string;
    tags?: { key?: string; label?: string }[];
    notifyCount?: number;
    unreadCount?: number;
    country?: string;
    access?: string;
    geographic?: {
      province?: { label?: string; key?: string };
      city?: { label?: string; key?: string };
    };
    address?: string;
    phone?: string;
    disabled?: boolean;
    username?: string;
    organization?: ORGANIZATION_API.Organization;
    role?: ROLE_API.Role;
  };

  type LoginParams = {
    username: string;
    password: string;
  };

  type UpdatePasswordParams = {
    old_password: string;
    new_password: string;
  };
}
