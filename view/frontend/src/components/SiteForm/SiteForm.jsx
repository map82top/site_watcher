import React, {useRef, useState} from 'react';
import "./SiteForm.scss";
import {
  Form,
  Input,
  Button,
  Select,
    List
} from 'antd';
import {useHistory} from "react-router-dom";
import { DeleteOutlined } from '@ant-design/icons';

const SiteForm = props => {
    const keyInput = useRef(null);
    const [keys, setKeys] = useState([]);
    const [keyListStatus, setKeyListStatus] = useState('');

    const history = useHistory();
    const onSubmit = values => {
        let message = {...values, "keys": keys}
        console.log("Send message " + JSON.stringify(message));
        window.socket.emit('save_site', message);
        history.replace("/");
    }

    const checkKeyListStatus = (rule, value, callback) => {
        try {
           if (keys.length === 0) {
                throw new Error('Something wrong!');
            }
            callback() // < -- this
          } catch (err) {
            callback(err);
          }
    }

    const onAddNewKey = () => {
        let value = keyInput.current && keyInput.current.state.value;

        if(!value || value.trim() === '') {
            return
        }
        if(!keys.includes(value)) {
            setKeys([...keys, value]);

            keyInput.current.state.value = '';
        }
    }

    const onDeleteKey = (key) => {
        setKeys(keys.filter((value, i) => value !== key));
    }

    return (
        <dev className="form-wrapper">
            <Form
                onFinish={onSubmit}
                layout="horizontal"
                className="form"
            >
                <Form.Item
                    className="form-item"
                    label="Name"
                    name="name"
                    rules={[{ required: true, message: 'Please input site name!' }]}
                >
                    <Input/>
                </Form.Item>
                <Form.Item
                    className="form-item"
                    label="URL"
                    name="url"
                    rules={[{ required: true, message: 'Please input site url!' }]}
                >
                    <Input/>
                </Form.Item>
                <Form.Item
                    className="form-item"
                    label="Regular check"
                    name="regular_check"
                    rules={[{ required: true, message: 'Please input site regular check!' }]}
                >
                  <Select>
                    <Select.Option value="TWICE_HOUR">30 minute</Select.Option>
                    <Select.Option value="ONCE_HOUR">1 hour</Select.Option>
                    <Select.Option value="FOUR_TIMES_DAY">6 hour</Select.Option>
                    <Select.Option value="TWICE_DAY">12 hour</Select.Option>
                    <Select.Option value="ONCE_DAY">24 hour</Select.Option>
                  </Select>
                </Form.Item>
                <Form.Item
                    className="form-item"
                    label="Check keys"
                    name="keys"
                    // validateStatus={keyListStatus}
                     rules={[{ validator: checkKeyListStatus, message: 'Not content any keys' }]}
                >
                    <List
                          className="form-item-key-list"
                          bordered
                          itemLayout="horizontal"
                          dataSource={keys}
                          renderItem={item => (
                            <List.Item
                                key={item}
                                 actions={[
                                  <Button type="primary"
                                       shape="round"
                                       icon={<DeleteOutlined className="table-body-action-button-icon"/>}
                                       className="form-item-key-list-delete-button"
                                          onClick={() => onDeleteKey(item)}/>
                                ]}
                            >
                               {item}
                            </List.Item>
                          )}
                    />
                    <div className="form-item-keys-input">
                        <Input ref={keyInput}/>
                        <Button
                            type="primary"
                            className="form-item-keys-input-add-button"
                            onClick={onAddNewKey}
                        >
                            Add
                        </Button>
                    </div>
                </Form.Item>
                 <Form.Item>
                    <Button
                        type="primary"
                        htmlType="submit"
                        className="form-submit-button"
                    >
                      Save
                    </Button>
                </Form.Item>
            </Form>
        </dev>
    )
}

export default SiteForm;