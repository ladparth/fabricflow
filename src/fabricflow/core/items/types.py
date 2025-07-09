"""
Microsoft Fabric item type definitions and enums.

This module defines the FabricItemType enum which contains all supported item types
that can be created and managed in Microsoft Fabric workspaces. These item types
represent the various resources and artifacts available in the Fabric platform.

Classes:
    FabricItemType: Comprehensive enum of all supported Microsoft Fabric item types.

The FabricItemType enum provides type safety and IntelliSense support when working
with different Fabric resources. Each enum value corresponds to the exact string
identifier used by the Microsoft Fabric REST API.

Item Categories:
    - Analytics: Reports, Dashboards, Semantic Models
    - Data Storage: Lakehouses, Warehouses, SQL Databases  
    - Data Processing: Data Pipelines, Dataflows, Notebooks
    - Development: Environments, Spark Job Definitions
    - Machine Learning: ML Models, ML Experiments
    - Real-time Analytics: Eventstreams, Eventhouses, KQL components
    - Integration: Copy Jobs, Mirrored resources

Example:
    ```python
    from fabricflow.core.items.types import FabricItemType
    from fabricflow.core.items.manager import FabricCoreItemsManager
    
    # Create a new Lakehouse
    manager = FabricCoreItemsManager(client, "MyWorkspace")
    lakehouse = manager.create_item(
        display_name="MyLakehouse",
        item_type=FabricItemType.LAKEHOUSE
    )
    
    # Create a data pipeline
    pipeline = manager.create_item(
        display_name="MyPipeline", 
        item_type=FabricItemType.DATA_PIPELINE,
        definition=pipeline_definition
    )
    ```

Note:
    This enum reflects the current Microsoft Fabric REST API item types.
    New item types may be added as Microsoft Fabric evolves.
    
    For the most up-to-date list, see:
    https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item
"""

from enum import Enum


class FabricItemType(Enum):
    APACHE_AIRFLOW_JOB = "ApacheAirflowJob"
    COPY_JOB = "CopyJob"
    DASHBOARD = "Dashboard"
    DATA_PIPELINE = "DataPipeline"
    DATAFLOW = "Dataflow"
    DATAMART = "Datamart"
    DIGITAL_TWIN_BUILDER = "DigitalTwinBuilder"
    DIGITAL_TWIN_BUILDER_FLOW = "DigitalTwinBuilderFlow"
    ENVIRONMENT = "Environment"
    EVENTHOUSE = "Eventhouse"
    EVENTSTREAM = "Eventstream"
    GRAPHQL_API = "GraphQLApi"
    KQL_DASHBOARD = "KQLDashboard"
    KQL_DATABASE = "KQLDatabase"
    KQL_QUERYSET = "KQLQueryset"
    LAKEHOUSE = "Lakehouse"
    ML_EXPERIMENT = "MLExperiment"
    ML_MODEL = "MLModel"
    MIRRORED_AZURE_DATABRICKS_CATALOG = "MirroredAzureDatabricksCatalog"
    MIRRORED_DATABASE = "MirroredDatabase"
    MIRRORED_WAREHOUSE = "MirroredWarehouse"
    MOUNTED_DATA_FACTORY = "MountedDataFactory"
    NOTEBOOK = "Notebook"
    PAGINATED_REPORT = "PaginatedReport"
    REFLEX = "Reflex"
    REPORT = "Report"
    SQL_DATABASE = "SQLDatabase"
    SQL_ENDPOINT = "SQLEndpoint"
    SEMANTIC_MODEL = "SemanticModel"
    SPARK_JOB_DEFINITION = "SparkJobDefinition"
    VARIABLE_LIBRARY = "VariableLibrary"
    WAREHOUSE = "Warehouse"
    WAREHOUSE_SNAPSHOT = "WarehouseSnapshot"
