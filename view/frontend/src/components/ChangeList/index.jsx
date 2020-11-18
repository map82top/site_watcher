import React, { useEffect, useState } from 'react';
import './ChangeList.scss';
import { Collapse } from 'antd';
import {useHistory, withRouter} from 'react-router-dom'
import io from "socket.io-client";
import {BackButton} from "../index";
const { Panel } = Collapse;

const Index = props => {
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
            const site_version = JSON.parse(json_site_version)
            site_version.content = JSON.parse(site_version.content)
            site_version.match_keys = JSON.parse(site_version.match_keys)
            site_version.differences = JSON.parse(site_version.differences)
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
                    </dl>
                </div>

            </div>
            <Collapse >
            {
                versions.map((version) => {
                    const innerContent = []
                    for(let selector in version.content) {
                        let content = version.content[selector]
                        let differences = version.differences[selector] ? version.differences[selector] : [];
                        let keys = version.match_keys[selector] ? version.match_keys[selector] : [];

                        keys.forEach(key => key.type = 'keyword');

                        let highlights = [...differences, ...keys]
                        highlights = highlights.sort((a, b) => a.start - b.start)
                        let markContent = '';
                        let startPosition = 0;
                        if(highlights.length > 0) {
                            for(let highlight of highlights) {
                                markContent = markContent + `${content.substring(startPosition, highlight.start)}<i class=${highlight.type}>${content.substring(highlight.start, highlight.end)}</i>`;
                                startPosition = highlight.end;
                            }
                        } else {
                            markContent = content
                        }
                        innerContent.push(
                            (<Collapse>
                                <Panel
                                    header={`Changes for ${selector} selector`}
                                    key={`${version.id}-${selector}`}
                                >
                                    <p dangerouslySetInnerHTML={{ __html: markContent }}></p>
                                </Panel>
                            </Collapse>)
                        )
                    }

                    return (
                        <Panel
                            header={`Watch in ${version.created_at} Changes: ${version.count_changes} Match keys: ${version.count_match_keys}`}
                            key={version.id}
                        >
                            {innerContent}
                        </Panel>
                    )
                })
            }
            </Collapse>
        </div>
    )
}

export default withRouter(Index);