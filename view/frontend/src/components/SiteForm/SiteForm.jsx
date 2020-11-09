import React, {useRef, useState, useEffect} from 'react';
import "./SiteForm.scss";
import {
  Form,
  Input,
  Button,
  Select,
    List
} from 'antd';
import {useHistory, withRouter} from "react-router-dom";
import { DeleteOutlined } from '@ant-design/icons';
import { checks } from "../../utils"

const SiteForm = props => {
    const {
        location
    } = props;

    const initialState = location.state ? {
                    "name": location.state.name,
                    "url": location.state.url,
                    "regular_check": location.state.regular_check,
                } : undefined;

    const keyInput = useRef(null);
    const [keys, setKeys] = useState(location.state ?  location.state.keys.split(/[\[\]\',]/).filter((value) => value.trim() !== '') : []);

    const history = useHistory();
    const onSubmit = values => {
        if(!location.state) {
            let message = {...values, "keys": keys}
            console.log("Send message " + JSON.stringify(message));
            window.socket.emit('save_site', message);
        } else {
            let message = {...values, "keys": keys, "id":location.state.id}
            console.log("Send message " + JSON.stringify(message));
            window.socket.emit('update_site', message);
        }

        history.replace("/");
    }

    const checkKeyListStatus = (rule, value, callback) => {
       if(keys.length === 0) {
           callback(new Object());
       }
    }

    const isValidURL = (rule, value, callback) => {
        debugger;
        if(!checks.isValidHttpUrl(value)) {
           callback(new Object());
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
        <div className="form-wrapper">
            <Form
                onFinish={onSubmit}
                layout="horizontal"
                className="form"
                initialValues={initialState}
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
                    rules={[{ required: true, message: 'URL is empty or incorrect!', validator: isValidURL }]}
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
        </div>
    )
}

export default withRouter(SiteForm);