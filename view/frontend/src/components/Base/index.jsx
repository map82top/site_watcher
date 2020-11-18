import React from 'react';
import { Layout } from 'antd';
import "./Base.scss"

const {Header, Footer, Content} = Layout;

const Index = ({children}) => {
    return (
        <Layout>
            <Header className="header">
                <div className="header-logo">Site Watcher</div>
            </Header>
            <Content className="content">
                {children}
            </Content>
        </Layout>
    )
};

export default Index;


