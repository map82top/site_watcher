import React, { useEffect, useState } from 'react';
import './ChangeList.scss';
import { Collapse } from 'antd';
import {useHistory, withRouter} from 'react-router-dom'
import io from "socket.io-client";
import {BackButton} from "../index";
const { Panel } = Collapse;

const ChangeList = props => {
    const {
        location
    } = props;

    const [versions, setVersions] = useState([])

    useEffect(() => {
        if(!window.socket) {
            window.socket = io();
        }
        window.socket.emit('get_versions', {"site_id": location.state.id})

        window.socket.on('site_version', json_site_version => {
            let site_version = JSON.parse(json_site_version)
            setVersions(versions => [...versions, site_version])
        })
    }, []);

    const history = useHistory();
    const onBack = () => {
        history.replace("/");
    }

    return (
        <div className="versions-body">
            <div className="versions-body-header">
                <BackButton onBack={onBack}/>
                <div>
                    <h1>List of watched versions of the <b>{location.state.name}</b> site</h1>
                    <h2>Legend</h2>
                    <dl className="versions-body-header-legend">
                        <dt>
                            <dd className="versions-body-header-legend-item">
                                <div className="versions-body-header-legend-item-color-box insert"/>
                                Insert
                            </dd>
                            <dd className="versions-body-header-legend-item">
                                <div className="versions-body-header-legend-item-color-box replace"/>
                                Replace
                            </dd>
                            <dd className="versions-body-header-legend-item">
                                <div className="versions-body-header-legend-item-color-box keyword"/>
                                Matched keyword
                            </dd>
                        </dt>
                    </dl>
                </div>

            </div>
            <Collapse >
            {
                versions.map((version) => {
                    let differences = JSON.parse(version.differences);
                    let keys = JSON.parse(version.match_keys);
                    keys.forEach(key => key.type = 'keyword');

                    let highlights = [...differences, ...keys]
                    highlights = highlights.sort((a, b) => a.start - b.start)

                    let markContent = '';
                    let startPosition = 0;
                    if(highlights.length > 0) {
                        for(let highlight of highlights) {
                            markContent = markContent + `${version.content.substring(startPosition, highlight.start)}<i class=${highlight.type}>${version.content.substring(highlight.start, highlight.end)}</i>`;
                            startPosition = highlight.end;
                        }
                    } else {
                        markContent = version.content
                    }

                    return (
                        <Panel
                            header={`Watch in ${version.created_at} Changes: ${version.count_changes} Match keys: ${version.count_match_keys}`}
                            key={version.id}
                        >
                            <p dangerouslySetInnerHTML={{ __html: markContent }}>
                            </p>
                        </Panel>
                    )
                })
            }
            </Collapse>
        </div>
    )
}

export default withRouter(ChangeList);