# Changelog

All notable changes to the JupyterHub deployment will be documented here. Any changes to the plugin itself will be 
documented in the [xnat-jupyter-plugin](https://bitbucket.org/xnatx/xnat-jupyterhub-plugin) repository.

## [1.2.0-rc] - 2024-06-05

### Added

- [JHP-82]: Support for named servers in JupyterHub. This will allow users to launch multiple servers from XNAT with
            different configurations.
- [JHP-93]: Add ipydatagrid to xnat/datascience-notebook image. Useful for dashboard development.

## [1.1.1] - 2024-05-03

- [JHP-81]: Add environmental variable for configuring TLS in the JupyterHub deployment. 
- [JHP-86]: Fix issue with volume name case sensitivity in helm chart pre_spawn_hook function.

## [1.1.0] - 2024-03-04

### Added

- Added changelog.
- [JHP-73]: Updates for dashboards. JupyterHub is now configured to accept a command from XNAT to launch a dashboard 
  container instead of only launching notebook containers. The xnat/datascience-notebook image is updated to include
  numerous packages for dashboard development, including Panel, Dash, Streamlit, and Voilà.
- [JHP-77]: Add GitHub workflows to build and publish the xnat/jupyterhub and xnat/data-science-notebook images to 
  Docker Hub. Repository has migrated from [Bitbucket](https://bitbucket.org/xnat-containers/xnat-jupyterhub/src/main/) 
  to [GitHub](https://github.com/NrgXnat/xnat-jupyterhub-image).

### Changed

- Updates to the helm chart to move python pre_spawn_hook, and other python code, to configmaps instead of managing it 
  in the values.yaml file. No behavior changes.

## [1.0.1] - 2023-10-12

### Added

- [JHP-67]: Adds a helm chart for deploying JupyterHub, configured to communicate with XNAT, to a Kubernetes cluster.

[JHP-67]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-67
[JHP-73]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-73
[JHP-77]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-77
[JHP-81]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-81
[JHP-82]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-82
[JHP-86]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-86
[JHP-93]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-93