import React from "react";
import { useHistory } from "react-router-dom";
import { Base, SiteForm, BackButton } from "../../components"
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
                <BackButton onBack={onBack}/>
                <h1 className="form-header-title">Create site watcher</h1>
            </div>
            <SiteForm />
        </Base>
    )
}

export default CreateSite;