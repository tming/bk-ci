#! /usr/bin/python3
import os
import re
import humps
import json

files = os.listdir('.')
replace_pattern = re.compile(r'__BK_[A-Z_]*__')
replace_dict = {}
config_parent = '../support-files/templates/'
template_parent = './helm-charts/templates/configmap/tpl/'

# 创建目录
os.system("mkdir -p "+template_parent)

# 设置一些默认值
default_value_dict = {
    'bkCiDataDir': '/data/dir/',
    'bkCiHttpPort': '80',
    'bkCiRedisDb': '0',
    'bkCiAuthProvider': 'sample',
    'bkCiLogStorageType': 'elasticsearch',
    'bkCiEsClusterName': 'devops',
    'bkCiProcessEventConcurrent': '10',
    'bkCiLogsDir': '/data/logs',
    'bkCiHome': '/data/bkee/ci',
    'bkCiGatewayDnsAddr': 'local=on'
}

default_value_dict.update(json.load(open('./values.json')))

# include 模板
include_dict = {
    '__BK_CI_MYSQL_ADDR__': '{{ include "bkci.mysqlAddr" . }}',
    '__BK_CI_MYSQL_USER__': '{{ include "bkci.mysqlUsername" . }}',
    '__BK_CI_MYSQL_PASSWORD__': '{{ include "bkci.mysqlPassword" . }}',
    '__BK_CI_REDIS_HOST__': '{{ printf "%s.%s.%s" (include "bkci.redisHost" .) .Release.Namespace "svc.cluster.local" | quote}}',
    '__BK_CI_REDIS_PASSWORD__': '{{ include "bkci.redisPassword" . }}',
    '__BK_CI_REDIS_PORT__': '{{ include "bkci.redisPort" . }}',
    '__BK_CI_ES_PASSWORD__': '{{ include "bkci.elasticsearchPassword" . }}',
    '__BK_CI_ES_REST_ADDR__': '{{ include "bkci.elasticsearchHost" . }}',
    '__BK_CI_ES_REST_PORT__': '{{ include "bkci.elasticsearchPort" . }}',
    '__BK_CI_ES_USER__': '{{ include "bkci.elasticsearchUsername" . }}',
    '__BK_CI_RABBITMQ_ADDR__': '{{ include "bkci.rabbitmqAddr" . }}',
    '__BK_CI_RABBITMQ_PASSWORD__': '{{ include "bkci.rabbitmqPassword" . }}',
    '__BK_CI_RABBITMQ_USER__': '{{ include "bkci.rabbitmqUser" . }}',
    '__BK_CI_RABBITMQ_VHOST__': '{{ include "bkci.rabbitmqVhost" . }}',
    '__BK_CI_INFLUXDB_HOST__': '{{ include "bkci.influxdbHost" . }}',
    '__BK_CI_INFLUXDB_PORT__': '{{ include "bkci.influxdbPort" . }}',
    '__BK_CI_INFLUXDB_USER__': '{{ include "bkci.influxdbUsername" . }}',
    '__BK_CI_INFLUXDB_PASSWORD__': '{{ include "bkci.influxdbPassword" . }}',
    '__BK_CI_INFLUXDB_ADDR__': 'http://{{ include "bkci.influxdbHost" . }}:{{ include "bkci.influxdbPort" . }}'
}

# 读取变量映射
env_file = open('../scripts/bkenv.properties', 'r')
value_re = re.compile(r'')
for line in env_file:
    if line.startswith('BK_'):
        datas = line.split("=")
        key = datas[0]
        replace_dict[key] = humps.camelize(key.lower())
env_file.close()

# 生成value.yaml
value_file = open('./helm-charts/values.yaml', 'w')
for line in open('./values.yaml', 'r'):
    value_file.write(line)
value_file.write('\nconfig:\n')
for key in sorted(replace_dict):
    default_value = '""'
    if key.endswith("PORT"):
        default_value = '80'
    value_file.write('  '+replace_dict[key]+': '+default_value_dict.get(replace_dict[key], default_value)+'\n')
value_file.flush()
value_file.close()

# 生成服务tpl
config_re = re.compile(r'-[a-z\-]*|common')
for config_name in os.listdir(config_parent):
    if config_name.endswith('yaml') or config_name.endswith('yml'):
        config_file = open(config_parent + config_name, 'r')
        the_name = config_re.findall(config_name)[0].replace('-', '', 1)
        new_file = open(template_parent+'_'+the_name+'.tpl', 'w')

        new_file.write('{{- define "bkci.'+the_name+'.yaml" -}}\n')
        for line in config_file:
            for key in replace_pattern.findall(line):
                if include_dict.__contains__(key):
                    line = line.replace(key, include_dict[key])
                else:
                    line = line.replace(key, '{{ .Values.config.'+replace_dict.get(key.replace('__', ''), '')+' }}')
            new_file.write(line)
        new_file.write('{{- end -}}')

        new_file.flush()
        new_file.close()
        config_file.close()

# 生成网关的configmap
gateway_envs = set()
for file in os.listdir(config_parent):
    if file.startswith('gateway'):
        for line in open(config_parent+file, 'r'):
            finds = replace_pattern.findall(line)
            for find in finds:
                gateway_envs.add(find)
gateway_config_file = open(template_parent+"/_gateway.tpl", "w")

gateway_config_file.write('{{- define "bkci.gateway.yaml" -}}\n')
for env in gateway_envs:
    if include_dict.__contains__(env):
        gateway_config_file.write(env.replace(
            "__", "")+": "+include_dict[env].replace(' . ', ' . | quote')+"\n")
    else:
        gateway_config_file.write(env.replace(
            "__", "")+": {{ .Values.config."+humps.camelize(env.replace("__", "").lower())+" | quote }}\n")
gateway_config_file.write('NAMESPACE: {{ .Release.Namespace }}\n')
gateway_config_file.write('SERVICE_PREFIX: {{ include "common.names.fullname" . }}\n')
gateway_config_file.write('{{- end -}}')

gateway_config_file.flush()
gateway_config_file.close()