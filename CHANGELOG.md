# Changelog

All notable changes to the JupyterHub deployment will be documented here. Any changes to the plugin itself will be 
documented in the [xnat-jupyter-plugin](https://bitbucket.org/xnatx/xnat-jupyterhub-plugin) repository.

## [Unreleased]

### Added

- Added changelog.
- [JHP-73]: Updates for dashboards. JupyterHub is now configured to accept a command from XNAT to launch a dashboard 
  container instead of only launching notebook containers. The xnat/datascience-notebook image is updated to include
  numerous packages for dashboard development, including Panel, Dash, Streamlit, and Voilà.
- [JHP-77]: Add GitHub workflows to build and publish the xnat/jupyterhub and xnat/data-science-notebook images to 
  Docker Hub.

### Changed

- Updates to the helm chart to move python pre_spawn_hook, and other python code, to configmaps instead of managing it 
  in the values.yaml file. No behavior changes.

## [1.0.1] - 2023-10-12

### Added

- [JHP-67]: Adds a helm chart for deploying JupyterHub, configured to communicate with XNAT, to a Kubernetes cluster.

[JHP-67]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-67
[JHP-73]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-73
[JHP-77]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-77