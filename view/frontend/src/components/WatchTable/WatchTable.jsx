import React, {useEffect, useState} from "react";
import { Table, Button, Tag } from 'antd';
import { AreaChartOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import "./WatchTable.scss"
import { useHistory } from "react-router-dom";
import io from "socket.io-client";
import {randomColor} from "randomcolor";
import {openNotification} from "../../utils";

const WatchTable = props => {
    const sites = {};
    const [listSites, setListSites] = useState([]);
    const history = useHistory();


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
            console.log('Deleted site')
            response = handleResponse(response)

            if (response.id) {
                delete sites[response.id];
                setListSites(getValues(sites));
            }
        });

        window.socket.on('update_response', (response) => {
            handleResponse(response)
        })

        window.socket.on('create_response', (response) => {
            handleResponse(response)
        })
    }, []);

    const handleResponse = (response) => {
         response = JSON.parse(response);
         debugger;
         openNotification({
                title: 'Result',
                text: response.message,
                type: response.status,
         });
         return response;
    }

    const  expandedRowRender = record => {
                          let versions = JSON.parse(record.versions)
                          return (
                                  <dl>
                                      <dt>Watch short description</dt>
                                      {versions.map((version) => <dd>{`Watch in  ${version.date} Changes: ${version.count_changes}
                                      Match keys: ${version.count_match_keys}`}</dd>)}
                                  </dl>
                          )
                        }

    const getValues = (object) => {
        return Object.keys(object).map(key => object[key]);
    }

    const onDelete = (record) => {
         window.socket.emit('delete_site', {"id": record.id });
    }

    const onVersionsStatistic = (record) => {
        history.replace({ pathname: "/versions_statistic", state: record })
    }

     const onCreateSite = () => {
        history.replace("/create_site");
    }

    const onUpdateSite = (record) => {
        debugger;
          history.replace({ pathname: "/update_site", state: record })
    }

    const columns = [
        {
            title: 'Name',
            dataIndex: 'name',
            sorter: {
              compare: (a, b) => a.name.localeCompare(b.name),
              multiple: 1,
            },
        },
        {
            title: 'URL',
            dataIndex: 'url',
             sorter: {
              compare: (a, b) => a.url.localeCompare(b.url),
              multiple: 1,
            },
        },
        {
            title: 'Status',
            dataIndex: 'status',
            render: status => {
                let text = status.charAt(0) + status.toLowerCase().slice(1);
                return text;
            },
            sorter: {
              compare: (a, b) => a.status.localeCompare(b.status),
              multiple: 1,
            },
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
             sorter: {
              compare: (a, b) => a.regular_check.localeCompare(b.regular_check),
              multiple: 1,
            },

            render: regular_check => {
                let text = undefined;
               switch(regular_check) {
                   case "TWICE_HOUR":
                       text = "Twice an hour";
                       break;
                   case "ONCE_HOUR":
                        text = "Once an hour";
                       break;
                   case "FOUR_TIMES_DAY":
                        text = "Four times a day";
                       break;
                   case "TWICE_DAY":
                       text = "Twice a day";
                       break;
                   case "ONCE_DAY":
                       text = "Once a day";
                       break;
                   default:
                       text = "Unknown";
                       break;
               }

                return text;
            }
        },
        {
            title: 'Last watch',
            dataIndex: 'last_watch',
            sorter: {
              compare: (a, b) => {
                  let a_date = new Date(a);
                  let b_date =  new Date(b);
                  if(a_date - b_date === 0) return 0;
                  else if(a_date - b_date > 0) return 1;
                  else return -1;
              },
              multiple: 1,
            },
            render: last_watch => {
                return !last_watch ? '-' : last_watch;
            }
        },
        {
            title: 'Count watches',
            dataIndex: 'count_watches',
            sorter: {
              compare: (a, b) => a.last_watch - b.last_watch,
              multiple: 1,
            },
        },
        {
            title: 'Created',
            dataIndex: 'created_at',
            sorter: {
              compare: (a, b) => {
                  let a_date = new Date(a);
                  let b_date =  new Date(b);
                  if(a_date - b_date === 0) return 0;
                  else if(a_date - b_date > 0) return 1;
                  else return -1;
              },
              multiple: 1,
            },
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
                           className="table-body-action-button"
                           onClick={() => onVersionsStatistic(record)}/>

                   <Button type="primary"
                       shape="round"
                       icon={<EditOutlined className="table-body-action-button-icon"/>}
                       className="table-body-action-button"
                           onClick={() => onUpdateSite(record)}/>

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
                    expandable={{
                    expandedRowRender: record => {
                          let versions = JSON.parse(record.versions)
                          return (
                                  <dl>
                                      <dt><h2>Watch short description</h2></dt>
                                      {versions.map((version) => <dd>{`Watch in  ${version.date} Changes: ${version.count_changes}
                                      Match keys: ${version.count_match_keys}`}</dd>)}
                                  </dl>
                          )
                        }
                    }}
                />
        </div>
    )
}

export default WatchTable;