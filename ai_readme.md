# BProxyPool Project Understanding

## Overview

BProxyPool is a proxy pool service implemented in Python. Its primary function is to manage a dynamic collection of proxy servers and provide them to client applications that require routing their network traffic through various IP addresses. This is commonly used for web scraping, data collection, or enhancing privacy.

## Key Features

*   **Virtual Pools (`virtual_pool`):** A standout feature is the concept of "virtual pools." This allows users to abstract multiple, logically independent proxy pools from a single, shared underlying proxy collection. This is highly beneficial for tasks like scraping different websites, as it enables the use of tailored proxy sets for each site, thereby optimizing proxy utilization and success rates.
*   **RESTful API:** The service exposes its functionalities through a RESTful API, providing a standardized way for applications to request proxies, report their status, and manage pools.
*   **Efficient Architecture:** BProxyPool is built using `asyncio` (for asynchronous I/O operations) and threading. This architecture allows it to handle numerous concurrent requests and network operations efficiently with minimal resource overhead.
*   **Extensibility:** The system is designed to be extensible, allowing users to integrate new proxy sources. This is achieved by creating custom Python classes that inherit from a base `BaseProxyGetter` class.

## Technology Stack

*   **Python:** The core application is written in Python (version 3.7+).
*   **Redis:** Redis serves as the backend data store for managing and persisting proxy information, including their availability and status.

## Core API Functionalities

The API provides several endpoints to interact with the proxy pool:

*   **Get Proxy:** Retrieve a random proxy from either the general pool or a specified `virtual_pool`.
*   **Delete Proxy:** Remove a proxy from the pool, typically if it's found to be non-functional.
*   **Cooldown Proxy:** Temporarily prevent a proxy within a `virtual_pool` from being selected for a defined period.
*   **Pool Status:** Fetch statistics and information about the proxy pool, such as the total number of proxies, their distribution across sources, and details of active `virtual_pools`.
*   **Manage Virtual Pools:** Create and delete `virtual_pools` as needed.

## Adding New Proxy Sources

To add new methods for discovering proxies:
1.  Navigate to the `proxy/` directory within the project.
2.  Create a new Python file (e.g., `my_new_source_getter.py`).
3.  In this file, define a class that inherits from `bproxypool.core.BaseProxyGetter`.
4.  Implement the required methods, particularly `get_proxy`, to fetch and return a list of proxy strings (e.g., `'127.0.0.1:8080'`).
5.  The framework will automatically discover and integrate this new source.

## Deployment

The typical deployment process involves:
1.  Cloning the BProxyPool repository.
2.  Installing Python dependencies listed in `requirements.txt`.
3.  Configuring project-specific settings in `config/frame_settings.py`.
4.  Optionally, adjusting Gunicorn (WSGI server) settings in `config/gunicorn.py`.
5.  Using the provided shell scripts (`start.sh`, `restart.sh`, `stop.sh`) to manage the two main components:
    *   **Scheduler:** Responsible for periodically fetching and validating proxies from the defined sources.
    *   **API Service:** The web service that provides API endpoints for proxy access and management.

In summary, BProxyPool provides a robust and flexible solution for managing and utilizing proxy servers, particularly catering to applications that can benefit from segmented proxy pools and easy integration of diverse proxy sources.
