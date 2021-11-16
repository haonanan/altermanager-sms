import os
import yaml
import urllib.error
import urllib.request
from flask import Flask, request
from datetime import datetime, timedelta


config_abs_path = '../config/config.yaml'


def config_load(path):
    """
    加载config.yml配置文件到内存中
    :param path:
    :return:
    """
    config = yaml.safe_load(open(path, 'r', encoding='utf-8'))
    return config


config_dict = config_load(config_abs_path)


def get_phone_list():
    """
    用于获取配置文件中的电话号码分组
    :return:返回一个字典,字典中key是分组名,values是电话号码
    """
    root_dir = "../config"
    config_path = os.path.join(root_dir, "config.yaml")
    if os.path.isfile(config_path):
        notice_type = config_dict['test']
        try:
            assert config_dict['prod_cfg']
            phone_dict = config_dict['prod']
            return phone_dict
        except KeyError:
            phone_dict = notice_type
            return phone_dict


# noinspection PyUnresolvedReferences
def call_sms_api(phone, context):
    root_dir = "../config"
    config_path = os.path.join(root_dir, "config.yaml")
    if os.path.isfile(config_path):
        url = config_dict['sms']['api_url']
        param = {
            "sname": config_dict['sms']['account'],
            "spwd": config_dict['sms']['password'],
            "scorpid": "",
            "sprdid": config_dict['sms']['sprdid'],
            "sdst": phone,
            "smsg": "【天府通】" + context
        }
        #数据准备
        data = urllib.parse.urlencode(param).encode(encoding='UTF8')
        #定义头
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        #开始提交数据
        req = urllib.request.Request(url, data, headers)
        urllib.request.urlopen(req)


def send_sms(context, group='operator'):
    phone_list = []
    phone_dict = get_phone_list()
    for keys, values in phone_dict.items():
        if keys == group:
            phone_list = values
    if len(phone_list) > 0:
        for phone_dict in phone_list:
            call_sms_api(phone_dict, context)


app = Flask("alermanager-sms")


@app.route('/health', methods=['GET'])
def health_check():
    """
    为k8s提供健康检查接口地址
    :return: 返回状态码200
    """
    return 'readiness', 200


@app.route('/alertmanager-sms', methods=['POST'])
def register():
    """
    解析alertmanager通过webhook提供的json字段,进行数据格式化,分组解析,将格式化后的正文,发送到不同分组
    """
    context = request.json
    for num in range(len(context['alerts'])):
        init_labels = context['alerts'][num]['labels']
        get_phone_list()
        init_annotations = context['alerts'][num]['annotations']
        _date = context['alerts'][num]['startsAt']
        date = datetime.strptime(_date, "%Y-%m-%dT%H:%M:%S.%fZ") + timedelta(hours=8)
        date = date.strftime("%Y/%m/%d %H:%M:%S")
        status = context['status']
        annotations_requir = ["description"]
        labels_require = ["container", "instance", "namespace", "pod"]
        alert_message_list = []
        if init_labels['severity'] != 'critical':
            app.logger.info(f'警告级别: {init_labels["severity"]} 警告内容: {init_annotations["summary"]}')
        else:
            if status == 'resolved':
                for key, value in init_annotations.items():
                    if key not in annotations_requir:
                        continue
                    else:
                        alert_message_list.append(f'k8s恢复: {value}')
            else:
                for key, value in init_annotations.items():
                    if key not in annotations_requir:
                        continue
                    else:
                        alert_message_list.append(f'k8s告警: {value}')
            app.logger.critical(f'警告级别: {init_labels["severity"]} 警告内容: {init_annotations["summary"]}')
            alert_message_list.append('[标识]')
            for key, value in init_labels.items():
                if key not in labels_require:
                    continue
                else:
                    alert_message_list.append(key + '：' + value)
            alert_message_list.append(f'time: {str(date)}')
            format_alert_message_list = "\n".join(alert_message_list)
            try:
                assert init_labels['namespace']
                group_list = init_labels['namespace'].split(",")
                group_list.append('operator')
                for element_group in group_list:
                    send_sms(context=format_alert_message_list, group=element_group)
            except KeyError:
                send_sms(context=format_alert_message_list)
    return 'message send  successfully'


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)