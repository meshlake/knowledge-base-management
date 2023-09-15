// import React, { useEffect, useState } from 'react';
// import styles from './index.less';
// import { Spin, Input, Button, Form } from 'antd';
// import classNames from 'classnames';
// import { EditOutlined } from '@ant-design/icons';
// import moment from 'moment';
// import ChangePassword from './Components/ChangePassword';

// const MyAccount: React.FC<{}> = () => {
//   const [user, setUser] = useState<API.UserDetails>({} as API.UserDetails);
//   const [loading, setLoading] = useState<boolean>(false);
//   const [editing, setEditing] = useState<boolean>(false);
//   const [visible, setVisible] = useState(false);

//   const [form] = Form.useForm();

//   const onEdit = () => {
//     form.setFieldsValue({ nickname: user.nickname });
//     setEditing(true);
//   };

//   useEffect(() => {
//   }, []);

//   return (
//     <div>
//       <Spin spinning={loading}>
//         <div className={styles.title}>个人中心</div>
//         <div className={styles.content}>
//           <div className={classNames(styles.item, styles.defaultSection)}>
//             <div className={styles.sectionTitle}>{myAccountIntl('loginSecurity')}</div>
//             <div className={styles.sectionContent}>
//               <div className={styles.contentTitle}>{myAccountIntl('password')}</div>
//               <div className={styles.contentDes}>{myAccountIntl('passwordDesc')}</div>
//               <Button
//                 type="link"
//                 onClick={() => {
//                   setVisible(true);
//                 }}
//                 className={styles.contentBtn}
//               >
//                 修改密码
//               </Button>
//             </div>
//           </div>
//         </div>
//       </Spin>
//       <ChangePassword visible={visible} closeModal={() => setVisible(false)}></ChangePassword>
//     </div>
//   );
// };

// export default MyAccount;
