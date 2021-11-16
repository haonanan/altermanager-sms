{{/*
Expand the name of the chart.
*/}}
{{- define "alertmanager-sms.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "alertmanager-sms.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "alertmanager-sms.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "alertmanager-sms.labels" -}}
{{ include "alertmanager-sms.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ include "alertmanager-sms.chart" . }}
{{- end }}

{{/* 
Service labels
*/}}
{{- define "alertmanager-sms.servicelabels" -}}
{{- if .Values.servicelabels -}}
name: {{ .Values.servicelabels }}
{{- else -}}
name: {{ include "alertmanager-sms.name" . }}
{{- end -}}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "alertmanager-sms.selectorLabels" -}}
app: {{ include "alertmanager-sms.name" . }}
version: stable
app.kubernetes.io/name: {{ include "alertmanager-sms.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "alertmanager-sms.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "alertmanager-sms.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/* 
create the namespace
*/}}
{{- define "alertmanager-sms.namespace" -}}
{{- if .Values.namespace -}}
namespace: {{ .Values.namespace }}  
{{- else -}}
{{- end -}}
{{- end -}}
