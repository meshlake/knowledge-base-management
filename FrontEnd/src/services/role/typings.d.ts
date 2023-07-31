declare namespace ROLE_API {
  type Role = {
    id: string;
    name: string;
    code: string;
    description: string;
  };

  type RoleCreate = Omit<Role, 'id'>;
}
