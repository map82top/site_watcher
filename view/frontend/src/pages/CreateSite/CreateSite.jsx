import React from "react";
import { useHistory } from "react-router-dom";
import { Base, SiteForm } from "../../components"
import "./CreateSite.scss"
import {LeftCircleOutlined} from "@ant-design/icons";
import {Button} from "antd";

const CreateSite = () => {
    const history = useHistory();
    const onBack = () => {
        history.replace("/");
    }

    return (
        <Base>
            <div className="form-header">
                <Button type="primary"
                        shape="round"
                        icon={<LeftCircleOutlined className="form-header-back-icon"/>}
                        className="form-header-back"
                        onClick={ onBack }
                />
                <h1 className="form-header-title">Create site watcher</h1>
            </div>
            <SiteForm />
        </Base>
    )
}

export default CreateSite;