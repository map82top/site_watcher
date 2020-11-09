import React from "react"
import "./BackButton.scss"
import {Button} from "antd";
import {LeftCircleOutlined} from "@ant-design/icons";

const BackButton = ({onBack}) => {
    return (
         <Button type="primary"
                        shape="round"
                        icon={<LeftCircleOutlined className="back-button-icon"/>}
                        className="back-button"
                        onClick={ onBack }
                />
    )
}

export default BackButton;