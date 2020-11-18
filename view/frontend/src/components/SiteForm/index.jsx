import React, {useRef, useState, useEffect} from 'react';
import "./SiteForm.scss";
import {
  Form,
  Input,
  Button,
  Select,
    List,
    Collapse
} from 'antd';
const { Panel } = Collapse;
import {useHistory, withRouter} from "react-router-dom";
import { DeleteOutlined } from '@ant-design/icons';
import { checks } from "../../utils"
import { InputList } from "../../components";

const Index = props => {
    const {
        location
    } = props;

    const convertToList = str_list => {
        return str_list.split(/[\[\]\',]/).filter((value) => value.trim() !== '');
    };

    const initialState = location.state ? {
                    "name": location.state.name,
                    "url": location.state.url,
                    "regular_check": location.state.regular_check,
                } : undefined;

    const [keys, setKeys] = useState(location.state ?  convertToList(location.state.keys) : []) ;
    const [selectors, setSelectors] = useState(location.state ?  convertToList(location.state.selectors) : []);

    const history = useHistory();
    const onSubmit = values => {
        if(!location.state) {
            let message = {...values, "keys": keys, "selectors": selectors}
            console.log("Send message " + JSON.stringify(message));
            window.socket.emit('save_site', message);
        } else {
            let message = {...values, "keys": keys, "selectors": selectors, "id":location.state.id}
            console.log("Send message " + JSON.stringify(message));
            window.socket.emit('update_site', message);
        }

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

     const checkSelectorsListStatus = (rule, value, callback) => {
        try {
           if (selectors.length === 0) {
                throw new Error('Something wrong!');
            }
            callback() // < -- this
          } catch (err) {
            callback(err);
          }
    }

    const isValidURL = (rule, value, callback) => {
         try {
           if (!checks.isValidHttpUrl(value)) {
                throw new Error('Something wrong!');
            }
            callback() // < -- this
          } catch (err) {
            callback(err);
          }
    }

    const selectorDescription = (
        <Collapse className="collection-list-description">
            <Panel header="Examples" key="1">
                <p><b>"p:nth-of-type(3)"</b> - find <i>3</i> tag p in the content</p>
                <p><b>"body a"</b> - find <i>a</i> tags beneath <i>body</i> tag</p>
                <p><b>".sister"</b> - find tag by CSS class</p>
                <p><b>"#link1"</b> - find tag by id</p>
                <p><b>"a[href="http://example.com/elsie"]"</b> - find tag by attribute value</p>

            </Panel>
        </Collapse>
    );

    const keysDescription = (
        <div className="collection-list-description">Any word or sentence</div>
    )


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
                    label="Search selectors"
                    name="selectors"
                    rules={[{ validator: checkSelectorsListStatus, message: 'Not content any selector' }]}
                >
                   <InputList
                       collection={selectors}
                       setCollection={setSelectors}
                       description={selectorDescription}
                   />
                </Form.Item>
                <Form.Item
                    className="form-item"
                    label="Check keys"
                    name="keys"
                    rules={[{ validator: checkKeyListStatus, message: 'Not content any key' }]}
                >
                     <InputList collection={keys} setCollection={setKeys} description={keysDescription}/>
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

export default withRouter(Index);