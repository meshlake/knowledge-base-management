declare namespace ORGANIZATION_API {
  type Organization = {
    id: string;
    name: string;
    code: string;
  };

  type OrganizationCreate = Omit<Organization, 'id'>;

  type OrganizationUpdate = Omit<Organization, 'code'>;
}
