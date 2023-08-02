import { DefaultFooter } from '@ant-design/pro-components';
import React from 'react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <DefaultFooter
      style={{
        background: '#fff',
      }}
      copyright={`${currentYear} 迈识AI出品`}
      links={[
        {
          key: 'Doc Search',
          title: '迈识AI机器人',
          href: '',
          blankTarget: true,
        },
      ]}
    />
  );
};

export default Footer;
