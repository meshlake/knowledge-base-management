import React from 'react';
import { Input } from 'antd';
import type { InputProps } from 'antd';

const TrimInput: React.FC<InputProps> = (props) => {
  const { onBlur, onChange } = props;
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    e.target.value = e.target.value?.trim();
    onBlur?.(e);
    onChange?.(e);
  };

  return <Input onBlur={handleBlur} {...props} autoComplete="off" />;
};

export default TrimInput;
