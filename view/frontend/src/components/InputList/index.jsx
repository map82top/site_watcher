import React, { useRef } from 'react';
import {Button, Input, List} from "antd";
import {DeleteOutlined} from "@ant-design/icons";
import "./InputList.scss";

const Index = ({collection, setCollection, description}) => {
    const itemInput = useRef(null);

    const onAddNewItem = () => {
        let value = itemInput.current && itemInput.current.state.value;

        if(!value || value.trim() === '') {
            return
        }
        if(!collection.includes(value)) {
            setCollection([...collection, value]);

            itemInput.current.state.value = '';
        }
    }

    const onDeleteItem = (item) => {
        setCollection(collection.filter((value, i) => value !== item));
    }

    return (
        <div className="input-list">
            {description ? <div className="input-list-description">{description}</div> : ''}

            <List
                  className="input-list-list"
                  bordered
                  itemLayout="horizontal"
                  dataSource={collection}
                  renderItem={item => (
                    <List.Item
                        key={item}
                         actions={[
                          <Button type="primary"
                               shape="round"
                               icon={<DeleteOutlined className="table-body-action-button-icon"/>}
                               className="input-list-list-delete-button"
                                  onClick={() => onDeleteItem(item)}/>
                        ]}
                    >
                       {item}
                    </List.Item>
                  )}
            />
            <div className="input-list-input">
                <Input ref={itemInput}/>
                <Button
                    type="primary"
                    className="input-list-input-add-button"
                    onClick={onAddNewItem}
                >
                    Add
                </Button>
            </div>
        </div>
    )
}

export default Index;