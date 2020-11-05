import React, {useEffect, useState} from "react";
import { Table, Button, Tag } from 'antd';
import { AreaChartOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import "./WatchTable.scss"
import { useHistory } from "react-router-dom";
import io from "socket.io-client";
import {randomColor} from "randomcolor";

const WatchTable = props => {
    const sites = {};
    const [listSites, setListSites] = useState([]);
    const history = useHistory();
    const onCreateSite = () => {
        history.replace("/create_site");
    }

    useEffect(() => {
        if(!window.socket) {
            window.socket = io();
        }

        window.socket.emit('get_sites');

        window.socket.on('site', (json_site) => {
            let site = JSON.parse(json_site);
            sites[site.id] = site;
            setListSites(getValues(sites))
        });

        window.socket.on('delete_response', (response) => {
            debugger;
            console.log('Deleted site')
            response = JSON.parse(response);
            if (response.id) {
                delete sites[response.id];
                setListSites(getValues(sites));
            }
        });
    }, []);


    const getValues = (object) => {
        return Object.keys(object).map(key => object[key]);
    }

    const onDelete = (record) => {
         window.socket.emit('delete_site', {"id": record.id });
    }

    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            // sorter: {
            //   compare: (a, b) => a.name > b.name,
            //   multiple: 1,
            // },
        },
        {
            title: 'Status',
            dataIndex: 'status',
            // sorter: {
            //   compare: (a, b) => a.status > b.status,
            //   multiple: 1,
            // },
        },
        {
            title: 'Keys',
            dataIndex: 'keys',
             render: keys => {
                let keysArray = keys.split(/[\[\]\',]/).filter((value) => value.trim() !== '');
                return (
                    <div>
                        {keysArray.map(key => {
                          let color = randomColor();
                          return (
                            <Tag color={color} key={key}>
                              {key}
                            </Tag>
                          );
                        })}
                    </div>
                )
             }
        },
        {
            title: 'Regular check',
            dataIndex: 'regular_check',
            // sorter: {
            //   compare: (a, b) => a.regular_check > b.regular_check,
            //   multiple: 1,
            // },
        },
        {
            title: 'Last watch',
            dataIndex: 'last_watch',
            // sorter: {
            //   compare: (a, b) => a.last_watch > b.last_watch,
            //   multiple: 1,
            // },
            render: last_watch => {
                return !last_watch ? '-' : last_watch;
            }
        },
        {
            title: 'Count watches',
            dataIndex: 'count_watches',
            // sorter: {
            //   compare: (a, b) => a.last_watch > b.last_watch,
            //   multiple: 1,
            // },
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            // sorter: {
            //   compare: (a, b) => a.last_watch > b.last_watch,
            //   multiple: 1,
            // },
        },
        {
            title: 'Action',
            dataIndex: 'id',
            key: "action",
            render: (text, record) => (
              <div>
                   <Button type="primary"
                           shape="round"
                           icon={<AreaChartOutlined className="table-body-action-button-icon"/>}
                           className="table-body-action-button"/>

                   <Button type="primary"
                       shape="round"
                       icon={<EditOutlined className="table-body-action-button-icon"/>}
                       className="table-body-action-button"/>

                   <Button type="primary"
                       shape="round"
                       icon={<DeleteOutlined className="table-body-action-button-icon"/>}
                       className="table-body-action-button"
                       onClick={() => onDelete(record)}/>

              </div>
             ),
        },
    ];


    return (
        <div className="table">
            <h1 className="table-title">Watching sites</h1>
                <Button
                    onClick={ onCreateSite }
                    className="table-add-button">
                    New site
                </Button>
                <Table
                    rowKey="id"
                    bordered={true}
                    pagination={false}
                    dataSource={listSites}
                    columns={columns}
                    className="table-body"
                    scroll={{ y: 600 }}
                />
        </div>
    )
}

export default WatchTable;