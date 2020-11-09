import React from "react";
import {BackButton, Base, ChangeList} from "../../components";
import {LeftCircleOutlined} from "@ant-design/icons";
import {Button} from "antd";
import {useHistory} from "react-router-dom";

const StatisticPage = props => {
    return (
        <Base>
            <ChangeList/>
        </Base>
    )
}

export default StatisticPage;