{{/*
Create the name of the postgres service account to use
*/}}
{{- define "jupyterhub.postgres.fullname" -}}
{{- printf "%s-%s" .Release.Name "postgres-rw" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "jupyterhub.postgres.postgresUri" -}}
{{- if .Values.postgres.external.postgresUri }}
{{- .Values.postgres.external.postgresUri }}
{{- else }}
{{- printf "%s-%s" .Release.Name "postgres-rw" | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end -}}

{{- define "jupyterhub.postgres.postgresPort" -}}
{{- if .Values.postgres.external.postgresPort }}
{{- .Values.postgres.external.postgresPort }}
{{- else }}5432
{{- end }}
{{- end -}}

{{- define "jupyterhub.postgres.postgresDatabase" -}}
{{- .Values.postgres.cluster.credentials.database }}
{{- end -}}

{{- define "jupyterhub.postgres.postgresUsername" -}}
{{- .Values.postgres.cluster.credentials.username }}
{{- end -}}

{{- define "jupyterhub.postgres.postgresPassword" -}}
{{- .Values.postgres.cluster.credentials.password }}
{{- end -}}

{{- define "jupyterhub.postgres.clusterName" -}}
{{- if .Values.postgres.cluster.name }}
{{- .Values.postgres.cluster.name }}
{{- else }}
{{- printf "%s-%s" .Release.Name "postgres" }}
{{- end }}
{{- end -}}
