# Changelog

All notable changes to the JupyterHub deployment will be documented here. Any changes to the plugin itself will be 
documented in the [xnat-jupyter-plugin](https://bitbucket.org/xnatx/xnat-jupyterhub-plugin) repository.

## [Unreleased]

### Added

- [JHP-75]: Update to JupyterLab 4.0.
- [JHP-76]: Update to JupyterHub 4.0.
- [JHP-96]: Add xnat/tensorflow-notebook image based on jupyter/tensorflow-notebook image. This image includes 
            TensorFlow and other helpful packages for working with XNAT data.
- [JHP-101]: Add pyradiomics to xnat/datascience-notebook and xnat/tensorflow-notebook images. This package is useful for 
             extracting radiomic features from DICOM images.
- [JHP-102]: Add highdicom to xnat/datascience-notebook. This package is useful for working with DICOM segmentation 
             objects and other DICOM objects.
- [JHP-113]: Add pygwalker to notebook images.

### Fixed

- [JHP-106]: From the JupyterHub 4.0 upgrade, add check_allowed method to the Authenticator class. The default behavior
             changes in version 5.0 so go ahead and add the method now instead of relying on the default behavior.
- [JHP-111]: From the JuptyerHub 4.0 upgrade, fix websocket http 403 error in JupyterLab. This is fixed by adding the 
             `JUPYTERHUB_SINGLEUSER_EXTENSION=0` environment variable to the JupyterHub deployment. Jupyter 5.0 has
             fixed this issue, but we are not quite ready to upgrade to 5.0 yet.

## [1.2.0] - 2024-06-27

### Added

- [JHP-82]: Support for named servers in JupyterHub. This will allow users to launch multiple servers from XNAT with
            different configurations.
- [JHP-93]: Add ipydatagrid to xnat/datascience-notebook image. Useful for dashboard development.
- [JHP-94]: Add dcmtk to xnat/datascience-notebook image. Useful for DICOM processing.

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
[JHP-75]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-75
[JHP-76]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-76
[JHP-77]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-77
[JHP-81]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-81
[JHP-82]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-82
[JHP-86]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-86
[JHP-93]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-93
[JHP-94]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-94
[JHP-96]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-96
[JHP-101]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-101
[JHP-102]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-102
[JHP-106]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-106
[JHP-111]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-111
[JHP-113]: https://radiologics.atlassian.net/jira/software/c/projects/JHP/issues/JHP-113