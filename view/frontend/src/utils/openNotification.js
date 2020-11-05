import { notification } from "antd";

export default ({ text, type = 'info', title, duration = 3 }) => {
    notification[type]({
        message: title,
        description: text,
        duration: duration,
    });

    setTimeout(() => {
       notification.destroy();
    }, duration * 1000)
}